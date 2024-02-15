from prompts.prompts import *
from core import AbstractControllerConfig, AbstractLLMConfig, AbstractRobotConfig, AbstractSimulaitonConfig
from typing import List


class SimulationConfig(AbstractSimulaitonConfig):
  render: bool = True
  debug: bool = True
  logging: bool = True
  env_name: str = "Cubes"     # [Cubes, CleanPlate, Sponge, MoveTable]
  task: str = "stack"  # [None, "stack", "pyramid", "L", "reverse", "clean_plate", "sponge", "move_table"]
  save_video: bool = False
  fps: int = 20 # only used if save_video = True
  dt: float = 0.05 # simulation timestep. Must be equal to that of controller
  frame_width: int = 512
  frame_height: int = 512
  frame_target_position: List[float] = [0.2, 0., 0.]
  frame_distance: float = 1.3
  frame_yaw: int = 90
  frame_pitch: int = -30


class TPConfig(AbstractLLMConfig):
  def __init__(self, task:str=None) -> None:
    self.mock_task = None # TODO wtf this is shit
    self.prompt: str = TP_PROMPTS[task] # TODO: this is bad. Only works for Optimization now
  avatar: str = "TP"
  model_name: str = "gpt-4"
  streaming: bool = False
  temperature: float = 0.9
  max_tokens: int = 500


class ODConfig(AbstractLLMConfig):
  def __init__(self, task:str=None) -> None:
    self.mock_task = None#"OD_move_table"
    self.prompt: str = OD_PROMPTS[task] # TODO: this is bad. Only works for NMPC now
  avatar: str = "OD"
  parsing: str = "optimization"
  model_name: str = "gpt-4"
  streaming: bool = False
  temperature: float = 0.6


class ControllerConfig(AbstractControllerConfig):
  nx: int = 3
  nu: int = 3 
  T: int = 15
  dt: float = 0.05
  lu: float = -0.2 # lower bound on u
  hu: float = 0.2  # higher bound on u
  model_type: str = "discrete"
  penalty_term_cons: float = 1e7
  

class RobotConfig(AbstractRobotConfig):
  def __init__(self, task:str=None) -> None:
    self.task: str = task
  name: str = "objective"
  tp_type: str = "plan_optimization"          # Task planner: ["plan_objective, plan_optimization"]
  od_type: str = "nmpc_optimization"          # Optimization Designer:  ["objective", "optimization"]
  controller_type: str = "optimization"  # Controller type:        ["objective", "optimization"]
  open_gripper_time: int = 15
  wait_s: float = 30. # wait time after a new MPC formualtion is applied

