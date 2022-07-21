try:
    from ulab import norm, zeros, array
except ImportError:
    from numpy import norm, zeros, array

MU = 3.986004418E5
R = 6371.009  # Earth's radius (km)
J2 = 1.08262668E-3  # J2 Value

def rk4(x, dt, f):
    """Runge-Kutta order 4 integration
    Args:
        - x: 6-vector, first 3 are position, last 3 are velocity
        - dt: time step
        - f: function defining the time derivative of x, ie: f(x)=dx

    Returns:
        - x: The integrated state
    """
    k1 = dt * f(x)
    k2 = dt * f(x + k1 / 2)
    k3 = dt * f(x + k2 / 2)
    k4 = dt * f(x + k3)
    return x + (1 / 6) * (k1 + 2 * k2 + 2 * k3 + k4)

def d_state(x):
    """Time derivative of the state variable
    Args:
        - x: 6-vector, first 3 are position (km), last 3 are velocity (km/s)
    Returns:
        - dx: 6-vector, first 3 are velocity (km/s), last 3 are acceleration (km/s^2) """
    pos = x[0:3]
    vel = x[3:6]

    # first we find the acceleration from two body
    # pos_norm = np.vector.sqrt(np.numerical.sum(pos ** 2))
    pos_norm = norm(pos)
    accel_twobody = -MU * (pos_norm ** -3) * pos

    # now we find the J2 acceleration

    accel_J2 = zeros(3)
    accel_J2[0] = -3 / 2 * J2 * MU * R ** 2\
        * pos_norm ** -5 \
        * pos[0] * (1 - 5 * pos[2] ** 2 / pos_norm ** 2)
    accel_J2[1] = -3 / 2 * J2 * MU * R ** 2\
        * pos_norm ** -5 \
        * pos[1] * (1 - 5 * pos[2] ** 2 / pos_norm ** 2)
    accel_J2[2] = -3 / 2 * J2 * MU * R ** 2\
        * pos_norm ** -5 \
        * pos[2] * (3 - 5 * pos[2] ** 2 / pos_norm ** 2)

    # add together accelerations
    # accel = accel_twobody + accel_J2
    accel = accel_twobody + accel_J2

    return array([vel[0], vel[1], vel[2], accel[0], accel[1], accel[2]])


def propogate(state, time_forward, integration_step=5):
    """Propogate the satelite state forward time_forward (s), in steps of integration_step (s) using rk4 integration.
    Takes into account spherical gravity and the J2 perturbation.
    Args:
        - state: 6-vector, first 3 are position (km), last 3 are velocity (km/s)
        - time_forward: time to propogate forward (s)
        - integration_step: time step for rk4 integration (s)
    Returns:
        - state: propogated state, 6-vector, first 3 are position (km), last 3 are velocity (km/s)
    """
    while time_forward > 0:
        dt = min(time_forward, integration_step)
        state = rk4(state, dt, d_state)
        time_forward -= dt
    return state