## NOT WORKING ##


# ~ from huggingface_hub import InferenceApi

# ~ # Replace 'your_token_here' with your Hugging Face API key
# ~ # ssbautomation@gmail.com, llmKey01, FINEGRAINED
# ~ api = InferenceApi(repo_id="EleutherAI/gpt-j-6B", token="hf_KNDmDiIzzms wkjSQkNwQZjPOImiSYshbSY")

# ~ # Input text for the LLM
input_text = "Once upon a time, in a faraway land, there was a"
# ~ input_text = "Who is the PM of the India"

# ~ # Call the API
# ~ response = api(inputs=input_text, parameters={"max_length": 100})
# ~ print(response)


from huggingface_hub import InferenceApi

# Replace 'your_token_here' with your Hugging Face API key
api = InferenceApi(repo_id="EleutherAI/gpt-j-6B", token="your_token_here")

# Input text and generation parameters
input_text = {
    "inputs": "Once upon a time, in a faraway land, there was a",
    "parameters": {
        "max_length": 100,  # Set the max length for generation
    },
}

# Call the API
response = api(inputs=input_text)
print(response)
