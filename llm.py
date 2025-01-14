from time import sleep
from typing import List, Optional
from core import AbstractLLM, AbstractLLMConfig
from mocks.mocks import nmpcMockOptions

import tiktoken
from streamlit import empty, session_state
from pydantic import BaseModel, Field
from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, AIMessage
from langchain.prompts.chat import SystemMessagePromptTemplate
from langchain.output_parsers import PydanticOutputParser
from langchain.callbacks.base import BaseCallbackHandler


TOKEN_ENCODER = tiktoken.encoding_for_model("gpt-4")

class Plan(BaseModel):
  tasks: List[str] = Field(description="list of all tasks to be carried out")
  
  def pretty_print(cls):
    pretty_msg = "Tasks:\n"
    for i, task in enumerate(cls.tasks):
      pretty_msg += f"{i+1}. {task}\n"
    return pretty_msg+'\n'

class Objective(BaseModel):
  objective: str = Field(description="objective function to be applied to MPC")

  def pretty_print():
    pass

class Optimization(BaseModel):
  objective: str = Field(description="objective function to be applied to MPC")
  equality_constraints: List[str] = Field(description="equality constraints to be applied to MPC")
  inequality_constraints: List[str] = Field(description="inequality constraints to be applied to MPC")

  def pretty_print(cls):
    pretty_msg = "Applying the following MPC fomulation:\n```\n"
    pretty_msg += f"min {cls.objective}\n"
    pretty_msg += f"s.t.\n"
    for c in cls.equality_constraints:
      pretty_msg += f"\t {c} = 0\n"
    for c in cls.inequality_constraints:
      pretty_msg += f"\t {c} <= 0\n"
    return pretty_msg+"\n```\n"

class StreamHandler(BaseCallbackHandler):

  def __init__(self, avatar:str, parser: PydanticOutputParser) -> None:
    super().__init__()
    self.avatar = avatar
    self.parser = parser

  def on_llm_start(self, serialized, prompts, **kwargs) -> None:
    """Run when LLM starts running."""
    self.text = ""
    self.container = empty()

  def on_llm_new_token(self, token: str, *, chunk, run_id, parent_run_id=None, **kwargs):
    super().on_llm_new_token(token, chunk=chunk, run_id=run_id, parent_run_id=parent_run_id, **kwargs)
    self.text += token
    self.container.write(self.text + "|")

  def on_llm_end(self, response, **kwargs):
    pretty_text = self.parser.parse(self.text).pretty_print()
    self.container.markdown(pretty_text, unsafe_allow_html=False)
    session_state.messages.append({"type": self.avatar, "content": pretty_text})

def simulate_stream(avatar:str, text:str, pretty_text:Optional[str]=None):
  """ Function used to simulate stream in case of harcoded GPT responses """
  placeholder = empty()
  # Simulate stream of response with milliseconds delay
  partial_text = ""
  for chunk in TOKEN_ENCODER.decode_batch([[x] for x in TOKEN_ENCODER.encode(text)]):
      partial_text += chunk
      sleep(0.05)
      # Add a blinking cursor to simulate typing
      placeholder.markdown(partial_text + "|")
  # store message in streamlit
  if pretty_text is None:
    placeholder.markdown(text)
    session_state.messages.append({"type": avatar, "content":text})
  else:
    placeholder.markdown(pretty_text)
    session_state.messages.append({"type": avatar, "content":pretty_text})  

ParsingModel = {
  "plan": Plan,
  "objective": Objective,
  "optimization": Optimization
}

class BaseLLM(AbstractLLM):

  def __init__(self, cfg: AbstractLLMConfig) -> None:
    super().__init__(cfg)
    # init parser
    self.parser = PydanticOutputParser(pydantic_object=ParsingModel[self.cfg.parsing])
    # init model
    self.model = ChatOpenAI(
      model_name=self.cfg.model_name, 
      temperature=self.cfg.temperature,
      streaming=self.cfg.streaming,
      callbacks=None if not self.cfg.streaming else [StreamHandler(self.cfg.avatar, self.parser)]
    )
    # init prompt
    system_prompt = SystemMessagePromptTemplate.from_template(self.cfg.prompt)
    self.messages = [system_prompt.format(format_instructions=self.parser.get_format_instructions())]    
    

  def run(self, user_message:str) -> str:
    self.messages.append(HumanMessage(content=user_message))
    if self.cfg.mock_task is None:
      model_message = self.model(self.messages)
    else:
      model_message = AIMessage(content=nmpcMockOptions[self.cfg.mock_task])
      text = model_message.content
      try:
        pretty_text = self.parser.parse(text).pretty_print()
      except:
        pretty_text = ""
      simulate_stream(self.cfg.avatar, text, pretty_text)
    self.messages.append(model_message)
    #print(f"\33[92m {model_message.content} \033[0m \n")
    return self.parser.parse(model_message.content)
