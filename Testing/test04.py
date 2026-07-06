from langchain_ollama import ChatOllama
# print("Initialized Normal chat")

# model = ChatOllama(model="qwen3.5:4b", temperature=0)

#
#
# # response = model.invoke("Why do parrots talk?")
# # print(response)
#
# for chunk in model.stream("Why do parrots have colorful feathers?"):
#     print(chunk.text, end="|", flush=True)
#
# print("Ended Normal chat")

print("Initialized 02 streaming, time based content")
import time

# model = ChatOllama(model="qwen3.5:4b", temperature=0, reasoning=False)
model = ChatOllama(model="qwen3.5:4b", temperature=0, reasoning=False, verbose=True)

start_time = time.perf_counter()
print(f"Start time: {start_time}")

# response = model.invoke("Why do parrots talk?")
# print(response)

# for chunk in model.stream("Why do parrots have colorful feathers?"):
# for chunk in model.stream("Hii"):
#     print(chunk.text, end="|", flush=True)
#     # print(chunk, end="|", flush=True)
#     # print(chunk)

response = model.invoke("Why do parrots talk?")
print(response)


end_time = time.perf_counter()

print(f"End time: {end_time}")

elapsed = end_time - start_time
print(f"Total execution time: {elapsed:.4f} seconds")

print("\nEnded 02 streaming, timebased conent")



# print("Initialized 03, custom model, ollama")
# import time
#
# model = ChatOllama(model="qwen3.5:4b", temperature=0)
#
# start_time = time.perf_counter()
# print(f"Start time: {start_time}")
#
# # # for chunk in model.stream("Why do parrots have colorful feathers?"):
# # for chunk in model.stream("Hii"):
# #     print(chunk.text, end="|", flush=True)
# import json
# import requests
#
# # ----------------------------
# # CONFIG (outside function)
# # ----------------------------
# url = "http://localhost:11434/api/chat"
# model = "qwen3.5:4b"
#
# messages = [
#     {"role": "user", "content": "Hi"}
# ]
#
# payload = {
#     "model": model,
#     "messages": messages,
#     "stream": True,
#     "think": False,
# }
#
# # ----------------------------
# # STREAM FUNCTION
# # ----------------------------
# def stream_ollama(url, payload):
#     response = requests.post(url, json=payload, stream=True, timeout=300)
#     response.raise_for_status()
#
#     result = ""
#
#     for line in response.iter_lines():
#         if not line:
#             continue
#
#         data = json.loads(line.decode("utf-8"))
#
#         if "message" in data:
#             content = data["message"].get("content", "")
#             if content:
#                 print(content, end="|", flush=True)
#                 result += content
#                 yield content
#
#         if data.get("done", False):
#             break
#
#     print()  # newline after stream
#     return result
#
#
# # ----------------------------
# # RUN
# # ----------------------------
# final_output = ""
#
# for chunk in stream_ollama(url, payload):
#     final_output += chunk
#
# print("\n\nFINAL OUTPUT:\n", final_output)
#
#
# end_time = time.perf_counter()
# print(f"End time: {end_time}")
# elapsed = end_time - start_time
# print(f"Total execution time: {elapsed:.4f} seconds")
# print("\nEnded 03, custom model, ollama")
#

# print("Initialized 04, custom ollama model")
# # import json
# # import requests
# # from langchain_core.language_models.llms import LLM
# # from typing import Iterator, Optional, List, Any
# #
# #
# # class CustomOllamaLLM(LLM):
# #     def __init__(self, url: str, model: str):
# #         super().__init__()
# #         self.url = url
# #         self.model = model
# #
# #     @property
# #     def _llm_type(self) -> str:
# #         return "custom_ollama"
# #
# #     def _call(self, prompt: str, stop: Optional[List[str]] = None, **kwargs: Any) -> str:
# #         payload = {
# #             "model": self.model,
# #             "messages": [{"role": "user", "content": prompt}],
# #             "stream": False,
# #             "think": False,
# #         }
# #
# #         response = requests.post(self.url, json=payload)
# #         response.raise_for_status()
# #
# #         data = response.json()
# #         return data["message"]["content"]
# #
# #     def stream(self, prompt: str) -> Iterator[str]:
# #         payload = {
# #             "model": self.model,
# #             "messages": [{"role": "user", "content": prompt}],
# #             "stream": True,
# #             "think": False,
# #         }
# #
# #         response = requests.post(self.url, json=payload, stream=True)
# #         response.raise_for_status()
# #
# #         for line in response.iter_lines():
# #             if not line:
# #                 continue
# #
# #             data = json.loads(line.decode("utf-8"))
# #
# #             if "message" in data:
# #                 chunk = data["message"].get("content", "")
# #                 if chunk:
# #                     yield chunk
# #
# import json
# import requests
# from typing import Optional, List, Any, Iterator
#
# from langchain_core.language_models.llms import LLM
#
#
#
# class ToolRegistry:
#     def __init__(self):
#         self.tools = {}
#
#     def register(self, name, func, description=""):
#         self.tools[name] = {
#             "func": func,
#             "description": description
#         }
#
#     def run(self, name, args):
#         return self.tools[name]["func"](**args)
#
#
#
# # class CustomOllamaLLM(LLM):
# #     url: str
# #     model: str
# #
# #     @property
# #     def _llm_type(self) -> str:
# #         return "custom_ollama"
# #
# #     def _call(
# #         self,
# #         prompt: str,
# #         stop: Optional[List[str]] = None,
# #         **kwargs: Any
# #     ) -> str:
# #
# #         payload = {
# #             "model": self.model,
# #             "messages": [{"role": "user", "content": prompt}],
# #             "stream": False,
# #             "think": False,
# #         }
# #
# #         response = requests.post(self.url, json=payload)
# #         response.raise_for_status()
# #
# #         data = response.json()
# #         return data["message"]["content"]
# #
# #     def stream(self, prompt: str) -> Iterator[str]:
# #         payload = {
# #             "model": self.model,
# #             "messages": [{"role": "user", "content": prompt}],
# #             "stream": True,
# #             "think": False,
# #         }
# #
# #         response = requests.post(self.url, json=payload, stream=True)
# #         response.raise_for_status()
# #
# #         for line in response.iter_lines():
# #             if not line:
# #                 continue
# #
# #             data = json.loads(line.decode("utf-8"))
# #
# #             chunk = data.get("message", {}).get("content", "")
# #             if chunk:
# #                 yield chunk
# #
#
#
# class CustomOllamaLLM(LLM):
#     # url: str
#     # model: str
#
#     url: str
#     model: str
#     bound_tools: dict = {}
#
#     def __init__(self, **data: Any):
#         super().__init__(**data)
#
#     # def __init__(self, url, model):
#     #     self.url = url
#     #     self.model = model
#     #     self.bound_tools = {}
#
#     @property
#     def _llm_type(self) -> str:
#         return "custom_ollama"
#
#     def bind_tools(self, tools: dict):
#         """
#         tools = {
#             "add": (func, "adds two numbers"),
#             "mul": (func, "multiplies numbers")
#         }
#         """
#         self.bound_tools = tools
#         return self
#
#     def _call(
#         self,
#         prompt: str,
#         stop: Optional[List[str]] = None,
#         **kwargs: Any
#     ) -> str:
#
#         payload = {
#             "model": self.model,
#             "messages": [{"role": "user", "content": prompt}],
#             "stream": False,
#             "think": False,
#         }
#
#         response = requests.post(self.url, json=payload)
#         response.raise_for_status()
#
#         data = response.json()
#         return data["message"]["content"]
#
#     def build_prompt(self, user_input):
#         tool_text = "\n".join(
#             [f"- {name}: {desc}" for name, (_, desc) in self.bound_tools.items()]
#         )
#
#         return f"""
# You are an assistant with tools.
#
# TOOLS:
# {tool_text}
#
# If you need a tool, respond ONLY in JSON:
# {{"tool": "...", "args": {{...}}}}
#
# User: {user_input}
# """
#
#     def stream(self, prompt: str) -> Iterator[str]:
#         payload = {
#             "model": self.model,
#             "messages": [{"role": "user", "content": prompt}],
#             "stream": True,
#             "think": False,
#         }
#
#         response = requests.post(self.url, json=payload, stream=True)
#         response.raise_for_status()
#
#         for line in response.iter_lines():
#             if not line:
#                 continue
#
#             data = json.loads(line.decode("utf-8"))
#
#             chunk = data.get("message", {}).get("content", "")
#             if chunk:
#                 yield chunk
#
#
#
#
# llm = CustomOllamaLLM(
#     url="http://localhost:11434/api/chat",
#     model="qwen3.5:4b"
# )
#
# # for token in llm.stream("Hii"):
# #     print(token, end="|", flush=True)
# #
#
# print("\nEnded 04, custom ollama model")
#
#
# print("Init 05, tools")
# from langchain.tools import tool
# from langchain_ollama import ChatOllama
# # from langchain.agents import initialize_agent, AgentType
#
# import json
#
# def run_with_tools(llm, registry, query):
#     prompt = llm.build_prompt(query)
#
#     response = llm.invoke(prompt)  # your existing request
#
#     try:
#         data = json.loads(response)
#
#         if "tool" in data:
#             tool_name = data["tool"]
#             args = data["args"]
#
#             result = registry.run(tool_name, args)
#
#             # send result back to model
#             final_prompt = f"""
# Tool result:
# {result}
#
# Now give final answer.
# """
#
#             return llm.invoke(final_prompt)
#
#     except Exception:
#         return response
#
#
# @tool
# def add(a: int, b: int) -> str:
#     """Add two numbers"""
#     return str(a + b)
#
#
# @tool
# def multiply(a: int, b: int) -> str:
#     """Multiply two numbers"""
#     return str(a * b)
#
#
# llm = CustomOllamaLLM(
#     url="http://localhost:11434/api/chat",
#     model="qwen3.5:4b"
# )
#
# tools = [add, multiply]
#
# registry = ToolRegistry()
# registry.register("add", add, "adds two numbers")
# registry.register("multiply", multiply, "multiplies two numbers")
#
# llm.bind_tools({
#     "add": (add, "adds two numbers"),
#     "multiply": (multiply, "multiplies two numbers")
# })
#
#
# output = run_with_tools(llm, registry, "What is 12 + 5 and 3 * 4?")
#
# # print(output)
#
# print(f"output: {output}")
#
# # agent = initialize_agent(
# #     tools=tools,
# #     llm=llm,
# #     agent=AgentType.CHAT_ZERO_SHOT_REACT_DESCRIPTION,
# #     verbose=True
# # )
#
# from langchain.agents import create_agent
#
# # agent = create_agent("openai:gpt-5.5", tools=tools)
# agent = create_agent(
#     tools=tools,
#     model=llm,
#     # agent=AgentType.CHAT_ZERO_SHOT_REACT_DESCRIPTION,
#     # verbose=True
# )
#
# # response = agent.invoke({
# #     "input": "What is 12 + 5 and 3 * 4?"
# # })
# #
# # print(response["output"])
# #
# # for chunk in agent.stream({
# #     "input": "What is 12 + 5 and 3 * 4?"
# # }):
# #     print(chunk)
#
# print("\nEnded 05, tools")
#
#
#
#
#
#
#
#
#
