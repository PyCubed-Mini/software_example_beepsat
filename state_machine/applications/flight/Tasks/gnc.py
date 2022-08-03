from lib.template_task import Task
from lib.control import bcross
import lib.pycubed as cubesat
from lib.IGRF import igrf_eci
from lib.sun_position import approx_sun_position_ECI
import lib.orbital_mechanics as orbital_mechanics
import lib.mekf as mekf
import time
try:
    from ulab.numpy import array
except ImportError:
    from numpy import array


def toStr(arr):
    return f'[{", ".join(map(str, arr))}]'

class task(Task):
    name = 'detumble'
    color = 'pink'

    rgb_on = False
    last = None
    eci_state = array([6871, -6571, -7071, 2, -10, 3])

    async def main_task(self):
        if self.last is None:
            self.last = time.monotonic()
            return

        t = time.monotonic()
        delta_t = t - self.last

        # update mekf
        w = cubesat.gyro()
        br_mag = cubesat.magnetic()
        br_sun = cubesat.sun_vector()
        nr_mag = igrf_eci(t, self.eci_state[0:3])
        nr_sun = approx_sun_position_ECI(t)
        mekf.step(w, delta_t, nr_mag, nr_sun, br_mag, br_sun)

        # propogate ECI position
        self.eci_state = orbital_mechanics.propogate(self.eci_state, delta_t, integration_step=5)

        # compute control
        m = bcross(cubesat.magnetic(), cubesat.gyro())

        # replace with calls to pycubed lib once it is ready
        if hasattr(cubesat, 'sim') and cubesat.sim():  # detects if we are hooked up to simulator
            print(f">>>m{toStr(m)}")
            print(f">>>t{time.monotonic_ns()}")

        self.last = time.monotonic()
