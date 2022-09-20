"""
Radio Task:

Manages all radio communication for the cubesat.
"""
from lib.template_task import Task
import radio_utils.transmission_queue as tq
import radio_utils.commands as cdh
import radio_utils.headers as headers
from pycubed import cubesat

ANTENNA_ATTACHED = False
CHUNK_BUFFER_SIZE = 1000

def should_transmit():
    """
    Return if we should transmit
    """
    return ANTENNA_ATTACHED and not tq.empty()

class task(Task):
    name = 'radio'
    color = 'teal'
    super_secret_code = b'p\xba\xb8C'

    def __init__(self):
        super().__init__()
        self.msg = ''

    async def main_task(self):
        if not cubesat.radio:
            self.debug('No radio attached, skipping radio task')
            return
        elif not ANTENNA_ATTACHED:
            self.debug('No antenna attached, skipping radio task')
            return

        if should_transmit():
            msg = tq.peek()
            packet, with_ack = msg.packet()
            self.debug(f'Transmission Queue {tq.queue}')

            debug_packet = str(packet)[:20] + "...." if len(packet) > 23 else packet
            self.debug(f"Sending packet: {debug_packet}")

            if with_ack:
                if await cubesat.radio.send_with_ack(packet):
                    msg.ack()
                else:
                    msg.no_ack()
            else:
                await cubesat.radio.send(packet, keep_listening=True)

            if tq.peek().done():
                tq.pop()
        else:
            self.debug("No packets to send")
            cubesat.radio.listen()
            response = await cubesat.radio.receive(keep_listening=True, with_ack=ANTENNA_ATTACHED, timeout=10)
            if response is not None:
                header = response[0]
                response = response[1:]  # remove the header byte

                self.debug(f'Recieved msg "{response}", RSSI: {cubesat.radio.last_rssi - 137}')

                if header == headers.NAIVE_START or header == headers.NAIVE_MID or header == headers.NAIVE_END:
                    self.handle_naive(header, response)
                elif header == headers.CHUNK_START or header == headers.CHUNK_MID or header == headers.CHUNK_END:
                    self.handle_chunk(header, response)
                elif header == headers.COMMAND:
                    self.handle_command(response)
            else:
                self.debug('No packets received')

        cubesat.radio.sleep()

    def handle_naive(self, header, response):
        if header == headers.NAIVE_START:
            txt = str(response, 'ascii')
            self.msg = txt
            self.last = txt
            print('Started recieving message')
        elif header == headers.NAIVE_MID:
            txt = str(response, 'ascii')
            if txt == self.last:
                print('Repeated message')
            else:
                self.msg += txt
                self.last = txt
                print('Continued recieving message')
        elif header == headers.NAIVE_END:
            txt = str(response, 'ascii')
            self.msg += txt
            self.debug('Finished recieving message')
            print(self.msg)
            self.try_write('/sd/naive.txt', 'w', self.msg)

    def handle_command(self, response):
        if len(response) < 6 or response[:4] != self.super_secret_code:
            return

        cmd = bytes(response[4:6])  # [pass-code(4 bytes)] [cmd 2 bytes] [args]
        cmd_args = bytes(response[6:])
        try:
            self.debug(f'cmd args: {cmd_args}', 2)
        except Exception as e:
            self.debug(f'arg decoding error: {e}', 2)

        if cmd in cdh.commands:
            try:
                if cmd_args:
                    self.debug(f'running {cdh.commands[cmd]} (with args: {cmd_args})')
                    cdh.commands[cmd](self, cmd_args)
                else:
                    self.debug(f'running {cdh.commands[cmd]} (no args)')
                    cdh.commands[cmd](self)
            except Exception as e:
                self.debug(f'something went wrong: {e}')
                cubesat.radio.send(str(e).encode())
        else:
            self.debug('invalid command!')
            cubesat.radio.send(b'invalid cmd' + cmd)

    def handle_chunk(self, header, response):
        if header == headers.CHUNK_START:
            self.cmsg = response
        elif header == headers.CHUNK_MID:
            self.cmsg += response
        elif header == headers.CHUNK_END:
            self.cmsg += response
        if len(self.cmsg) > CHUNK_BUFFER_SIZE or header == headers.CHUNK_END:
            self.try_write('/sd/chunk.txt', 'a', self.cmsg)
            self.cmsg = None

    def try_write(self, file, mode, data):
        if not cubesat.sdcard or not cubesat.vfs:
            self.debug('No SD card attached, skipping writing to file')
            return
        try:
            f = open(f"/sd/{file}", mode)
            f.write(data)
            f.close()
            self.debug('Sucesfully wrote to file')
        except Exception as e:
            self.debug(f'Error while writing to file {e}')
