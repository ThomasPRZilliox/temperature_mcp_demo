import time
import threading
from enum import Enum
import numpy as np

class ControllerState(Enum):
    IDLE = 0
    HEATING = 1
    COOLING = 2
class TemperatureState:
    def __init__(self):
        self.current = 20.0
        self.controller_state = ControllerState(0)
        self.lock = threading.Lock()

noise_low = -0.05
noise_high = 0.05
def temperature_controller(state: TemperatureState, stop_event: threading.Event):
    while not stop_event.is_set():
        with state.lock:
            if state.controller_state == ControllerState.IDLE:
                # state.current = float(state.current + np.random.uniform(low=-0.1, high=0.1, size=20))
                state.current += np.random.uniform(low=noise_low, high=noise_high)
            elif state.controller_state == ControllerState.HEATING:
                increase = 0.5 + np.random.uniform(low=noise_low, high=noise_high)
                state.current += increase
            elif state.controller_state == ControllerState.COOLING:
                decrease = 0.5 + np.random.uniform(low=noise_low, high=noise_high)
                state.current -= decrease
            else:
                state.current = 0.0

        time.sleep(1)  # control loop period (1s)
