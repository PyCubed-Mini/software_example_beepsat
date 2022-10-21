from Tasks.safety import task as safety
from Tasks.beacon_task import task as beacon
from Tasks.blink_task import task as blink
from Tasks.imu_task import task as imu
from Tasks.time_task import task as time
from Tasks.gnc import task as gnc
from Tasks.radio import task as radio
from TransitionFunctions import announcer, low_power_on, low_power_off
from states import config  # noqa: F401

TaskMap = {
    "Safety": safety,
    "Beacon": beacon,
    "Blink": blink,
    "IMU": imu,
    "Time": time,
    "GNC": gnc,
    "Radio": radio,
}

TransitionFunctionMap = {
    'Announcer': announcer,
    'LowPowerOn': low_power_on,
    'LowPowerOff': low_power_off,
}
