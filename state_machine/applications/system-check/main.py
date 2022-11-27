"""
Python System Check Module for PyCubed Mini satellite board
"""

import tests
import tests.i2c_scan
import tests.nvm_access_test
import tests.logging_infrastructure_test
import tests.sd_test
import tests.imu_test
import tests.sun_sensor_test
import tests.coil_test
import tests.burnwire_test
import supervisor
import tasko
from print_utils import bold, normal, red, green

supervisor.disable_autoreload()

# initialize hardware_dict and result_dict
result_dict = dict()

"""
Each test group contains:
    - full name
    - nick name
    - class reference
    - if it is to be run in default mode
"""
all_tests = [
    ("Delete Logs and Test SD Card", "sd", tests.sd_test, True),
    ("IMU Test", "imu", tests.imu_test, True),
    ("Sun Sensor Test", "sun", tests.sun_sensor_test, True),
    ("Coil Driver Test", "coil", tests.coil_test, True),
    ("Burnwire Test", "burn", tests.burnwire_test, False),
    ("I2C_Scan", "i2c", tests.i2c_scan, False),
    ("Reset and Test NVM", "nvm", tests.nvm_access_test, True),
    ("Delete Logs and Test Logging Infrastructure", "log",
     tests.logging_infrastructure_test, True),
]


def test_options(tests):
    print(f'\n\nSelect: {bold}(a){normal} for all, {bold}(d){normal} ' +
          'for default, or select a specific test:')
    for (name, nick, _, _) in tests:
        print(f"  {bold}({nick}){normal}: {name}")


def results_to_str(results):
    failed = []
    passed = []
    for (test_name, (test_description, test_success)) in results.items():
        if test_success is not None:
            if test_success:
                passed.append(f"{test_name}: {test_description}")
            else:
                failed.append(f"{test_name}: {test_description}")
    newline = '\n'  # f strings can't contain \

    def bullet(str):
        '''Utility to a bullet point before a string'''
        return f'  - {str}'

    return f"""{red}{bold}Failed Tests:{normal}
{newline.join(map(bullet, failed))}
{green}{bold}Passed Tests:{normal}
{newline.join(map(bullet, passed))}"""


async def main_test():
    test_options(all_tests)
    choice = input("~> ")
    if choice == 'a' or choice == 'd':
        for (_, _, test, default) in all_tests:
            if (choice == 'a' or default):
                await test.run(result_dict)
    else:
        for (_, nick, test, _) in all_tests:
            if choice == nick:
                await test.run(result_dict)
                break
        else:
            print('Invalid selection')

    print(results_to_str(result_dict))

tasko.add_task(main_test(), 1)
tasko.run()
