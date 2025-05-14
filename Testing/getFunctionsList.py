import inspect
import baseTemp  # import your file (without .py extension)

# Get the class from the module
cls = baseTemp.BaseChatOpenAI

# Get only the function names
function_names = [name for name, member in inspect.getmembers(cls, inspect.isfunction)]

print(function_names)
