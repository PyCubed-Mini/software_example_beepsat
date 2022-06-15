# check for low battery condition

from lib.template_task import Task


class task(Task):
    name = 'vbatt'
    color = 'orange'

    timeout = 60 * 60  # 60 min

    async def main_task(self):
        # Tasks have access to the cubesat object, and can get readings like battery voltage
        self.debug(f'Current battery voltage: {self.cubesat.battery_voltage}')