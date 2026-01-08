from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from pydantic import BaseModel, Field
import numpy as np
from enum import Enum
import threading
from temperature_controller import temperature_controller, TemperatureState,ControllerState

api = FastAPI()

# For DEMO only this should not be set in production
api.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


##################
# Pydantic class #
##################

class Temperature(BaseModel):
    temperature : float

class ControllerStateRequest(BaseModel):
    state: ControllerState = Field(...,description= "State of the controller 0=Idle, 1=Heating and 2=Cooling")

class ControllerStateResponse(BaseModel):
    controller_state: ControllerState
    current_temperature: float

################
# Shared state #
################
state = TemperatureState()

############
# Threads #
############
stop_event = threading.Event()
controller_thread = threading.Thread(
    target=temperature_controller,
    args=(state, stop_event),
    daemon=True,  # dies with the app
)

@api.on_event("startup")
def startup_event():
    controller_thread.start()

@api.on_event("shutdown")
def shutdown_event():
    stop_event.set()
    controller_thread.join()

@api.get('/')
def index():
    return {"message":"Welcome to the temperature controller demo"}


@api.get('/temperature')
def get_temperature():
    with state.lock:
        return {
            "current": state.current
        }

@api.get('/controller_state')
def get_state():
    with state.lock:
        return {
            "state": state.controller_state
        }

@api.get('/data', response_model=ControllerStateResponse)
def get_state():
    with state.lock:
        return {
            "controller_state": state.controller_state,
            "current_temperature": state.current
        }


@api.put('/controller_state', response_model=ControllerStateResponse)
def set_controller_state(controller_state_request: ControllerStateRequest):
    with state.lock:
        state.controller_state = controller_state_request.state
        return {
            "controller_state": state.controller_state,
            "current_temperature": state.current
        }


