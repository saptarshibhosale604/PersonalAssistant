
import os

def RemoveSpaces(input_string):
    # Remove spaces from the input string
    return input_string.replace(" ", "")

openai_key = "sk-proj-zP6XLa1m5gtlBcXJCaHZGmAvXEvUrP 5ATJSPBfLRdEuF-vSroLAG4V0zBdpwPz9PTXe9rM0-CgT3BlbkFJ83 AZyS7Zds5OT4G7S7MJslTok1O8P7ftX6Zz_IvdtMsy_CnjJeBoOv-o-G5t13-1Yw20ei_BwA" # myTestKey08, saptarshibhosale604@gmail.com
tavily_key = "tvly-kX76LCz C36oih0u9COcf6oa 53A47MX0g"

os.environ["OPENAI_API_KEY"] = RemoveSpaces(openai_key)
os.environ["TAVILY_API_KEY"] = RemoveSpaces(tavily_key)



from ollama import chat
from ollama import ChatResponse


# print("initialized")
def CustomOllama(userInput):

	# simple one question answer
	response: ChatResponse = chat(model='llama3.2:1b', messages=[
	{
		'role': 'user',
		'content': userInput,
	},
	])
	# print(response['message']['content'])
	# or access fields directly from the response object
	print(f"CustomOllama: {response.message.content}")
	humanBreak = input("humanBreak03:")
	return response.message.content




# from langchain_core.outputs import ChatGeneration, ChatGenerationChunk, ChatResult
# from langchain_core.language_models import BaseChatModel


# from typing import Any, Sequence, Optional, Union, Callable, Dict
# # from langchain_core.chat_models.base import BaseChatModel, ChatResult
# from langchain_core.schema import BaseMessage
# from langchain_core.callbacks.manager import CallbackManagerForLLMRun
# from langchain_core.tools import BaseTool
# from langchain_core.utils.function_calling import convert_to_openai_tool
# import warnings
from langchain_openai import ChatOpenAI

from typing import Any, Dict, Iterator, List, Optional, Literal

from langchain_core.callbacks import (
    CallbackManagerForLLMRun,
)
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import (
    AIMessage,
    AIMessageChunk,
    BaseMessage,
)
from langchain_core.messages.ai import UsageMetadata
from langchain_core.outputs import ChatGeneration, ChatGenerationChunk, ChatResult
from pydantic import Field

from typing import Sequence, Union, Callable, Type
from langchain_core.tools import BaseTool
from langchain_core.utils.function_calling import convert_to_openai_tool

# User-provided function for custom generation
# from custom_ollama_module import CustomOllama

class ChatParrotLink(BaseChatModel):
    """
    Custom LLM wrapper that delegates generation to CustomOllama if defined,
    otherwise falls back to OllamaClient usage.
    """
    model_name: str = Field(alias="model")
    """The name of the model"""
    parrot_buffer_length: int
    """The number of characters from the last message of the prompt to be echoed."""
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    timeout: Optional[int] = None
    stop: Optional[List[str]] = None
    max_retries: int = 2

    def __init__(
        self,
        model_name: str = "parrot-link",
        temperature: float = 0.7,
        # streaming: bool = False,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.model_name = model_name
        self.temperature = temperature
        # self.streaming = streaming
        self._tools: list[dict] = []  # initialized empty

    def bind_tools(
        self,
        tools: Sequence[Union[Dict[str, Any], type, Callable, BaseTool]],
        *,
        tool_choice: Optional[
            Union[Dict, str, Literal["auto", "none", "required", "any"], bool]
        ] = None,
        strict: Optional[bool] = None,
        parallel_tool_calls: Optional[bool] = None,
        **kwargs: Any,
    ) -> "ChatParrotLink":
        formatted = [convert_to_openai_tool(t, strict=strict) for t in tools]
        names = [f.get("function", {}).get("name", f.get("name")) for f in formatted]
        if tool_choice:
            if isinstance(tool_choice, str) and tool_choice in names:
                tool_choice = {"type": "function", "function": {"name": tool_choice}}
            elif tool_choice == "any":
                tool_choice = "required"
            elif isinstance(tool_choice, bool):
                tool_choice = "required"
            elif not isinstance(tool_choice, dict):
                raise ValueError(f"Invalid tool_choice: {tool_choice}")
            kwargs["tool_choice"] = tool_choice
        self._tools = formatted
        return self

    def _generate(
        self,
        messages: list[BaseMessage],
        stop: Optional[list[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> ChatResult:
        # If user defined CustomOllama, use it exclusively
        try:
            # Concatenate user messages into a single input string
            user_input = "\n".join([msg.content for msg in messages])
            response_text = CustomOllama(user_input)
            return ChatResult(generations=[[BaseMessage(content=response_text)]])
        except Exception:
            # Fallback to default if CustomOllama fails
            payload = {
                "model": self.model_name,
                "messages": [msg.dict() for msg in messages],
                "temperature": self.temperature,
                **kwargs,
            }
            if stop:
                payload["stop"] = stop
            if self._tools:
                payload["functions"] = self._tools
                if "tool_choice" in kwargs:
                    payload["function_call"] = kwargs["tool_choice"]
            warnings.warn("CustomOllama failed, using default OllamaClient flow.")
            # Insert OllamaClient logic here or raise
            raise RuntimeError("CustomOllama invocation failed and no default client is configured.")

    @property
    def _llm_type(self) -> str:
        """Get the type of language model used by this chat model."""
        return "echoing-chat-model-advanced"

    @property
    def _default_params(self) -> dict[str, Any]:
        """Get the default parameters for calling OpenAI API."""
        exclude_if_none = {
            "presence_penalty": self.presence_penalty,
            "frequency_penalty": self.frequency_penalty,
            "seed": self.seed,
            "top_p": self.top_p,
            "logprobs": self.logprobs,
            "top_logprobs": self.top_logprobs,
            "logit_bias": self.logit_bias,
            "stop": self.stop or None,  # also exclude empty list for this
            "max_tokens": self.max_tokens,
            "extra_body": self.extra_body,
            "n": self.n,
            "temperature": self.temperature,
            "reasoning_effort": self.reasoning_effort,
            "service_tier": self.service_tier,
        }

        params = {
            "model": self.model_name,
            # "stream": self.streaming,
            **{k: v for k, v in exclude_if_none.items() if v is not None},
            **self.model_kwargs,
        }

        return params

    # The following methods (_from_response, _from_stream) can be removed if not used





# llm = ChatParrotLink(parrot_buffer_length=3, model="my_custom_model_02")
# llmRaw = ChatParrotLink(parrot_buffer_length=3, model="my_custom_model_02")
# llm = llmRaw.bind_tools(tools) # not working as expected

## Open AI LLM model
llm = ChatOpenAI(model="gpt-3.5-turbo", max_tokens=500, temperature=0, max_retries=1)

print(f"CustomLLM llm: {llm}::")



from pydantic import BaseModel, Field


class GetWeather(BaseModel):
    '''Get the current weather in a given location'''

    location: str = Field(
        ..., description="The city and state, e.g. San Francisco, CA"
    )


class GetPopulation(BaseModel):
    '''Get the current population in a given location'''

    location: str = Field(
        ..., description="The city and state, e.g. San Francisco, CA"
    )


llm_with_tools = llm.bind_tools(
    [GetWeather, GetPopulation]
    # strict = True  # enforce tool args schema is respected
)

ai_msg = llm_with_tools.invoke(
    "Which city is hotter today and which is bigger: LA or NY?"
)
ai_msg.tool_calls

print(f"ai_msg: {ai_msg}")
print("#########################")
print(f"ai_msg.tool_calls: {ai_msg.tool_calls}")