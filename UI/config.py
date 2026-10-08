
modeConfigFilePath = "./UI/modesConfig.json"
modeConfigSandboxFilePath = "./UI/modesConfigSandbox.json"
modeSandboxLocal = "false"

# Create file with default configuration
defaultConfig = {
    'mode-llm': 'globalGemini01',
    'mode-stream': 'false',
    'mode-conversation': 'wakeUp',
    'mode-input': 'text',
    'mode-output': 'text',
    'mode-context': 'yes',
    'mode-framework': 'langchain',
    'mode-sandbox': 'false',
    'mode-tools': 'update',
    'mode-reset': 'now',
    'mode-os': 'windows'
}

modeConfigInitializationJson = {
    'mode-llm': {
        'current': 'local',
        'allowed': {
            'local': 'Model running locally, Jarvis like personality',
            'local-4b': 'Model running locally, qwen3.5:4b',
            'local-4b-no-tools': 'Model running locally, qwen3.5:4b, without any agent tools',
            'local-buddy': 'Model running locally with Best bud personality',
            'globalChatgpt01': 'Model running on cloud / chatgpt gpt-5.5, for plan generation',
            'globalChatgpt02': 'Model running on cloud / chatgpt gpt-5.4, for plan execution',
            'globalGemini01': 'Model running on cloud / Google gemini-3.6-flash, best (planning + complex tools)',
            'globalGemini02': 'Model running on cloud / Google gemini-3.5-flash-lite, 2nd best (fast, simple tasks)',
            'globalMistral01': 'Model running on cloud / Mistral mistral-small-latest, balanced primary option with tool support',
            'globalMistral02': 'Model running on cloud / Mistral ministral-8b-latest, faster lightweight fallback',
            'globalGroq01': 'Model running on cloud / Groq openai/gpt-oss-120b, strong reasoning/planning',
            'globalGroq02': 'Model running on cloud / Groq qwen/qwen3.8-27b, fast fallback for general tasks',
            'globalOpenRouter01': 'Model running on cloud / OpenRouter nvidia/nemotron-3-ultra-550b-a55b:free stronger planning + tool use',
            'globalOpenRouter02': 'Model running on cloud / OpenRouter nvidia/nemotron-3.5-lightning:free, faster fallback / general tasks',
            'globalHuggingFace01': 'Model running on cloud / Hugging Face model 01 (Mistral / Llama)',
            'globalHuggingFace02': 'Model running on cloud / Hugging Face model 02 (Qwen / Phi)'
        }
    },
    'mode-stream': {
        'current': 'false',
        'allowed': {
            'false': 'llm streaming mode off',
            'true': 'llm streaming mode on',
        }
    },
    'mode-conversation': {
        'current': 'wakeUp',
        'allowed': {
            'sleep': 'Go to Hibernate',
            'wakeUp': 'Going to answer the user input'
        }
    },
    'mode-input': {
        'current': 'text',
        'allowed': {
            'text': 'Text input mode',
            'speech': 'Speech input mode',
            'file': 'Read from the userInput.txt file',
            'multi': 'Text input mode multi'
        }
    },
    'mode-output': {
        'current': 'text',
        'allowed': {
            'text': 'Text output mode',
            'speech': 'Speech output mode'
        }
    },
    'mode-context': {
        'current': 'yes',
        'allowed': {
            'no': 'No context in conversation',
            'yes': 'The conversation understands the context'
        }
    },
    'mode-framework': {
        'current': 'langchain',
        'allowed': {
            'langchain': 'Use langchain agent',
            'fabric': 'Use fabric'
        }
    },
    'mode-sandbox': {
        'current': 'false',
        'allowed': {
            'true': 'follow the local/sandbox mode config file',
            'false': 'follow the global mode config file'
        }
    },
    'mode-tools': {
        'current': 'update',
        'allowed': {
            'get': 'Get list of tools',
            'update': 'Update the list of tools'
        }
    },
    'mode-reset': {
        'current': 'now',
        'allowed': {
            'now': 'Mode reset now',
        }
    },
    'mode-os': {
        'current': 'windows',
        'allowed': {
            'windows': 'Windows OS - prepend POWERSHELL CMD prefix to first input',
            'linux': 'Linux OS - no prefix added'
        }
    }
}

# Preset 1: Development Mode
presetDevelopment = {
    'mode-llm': 'local',
    'mode-conversation': 'wakeUp',
    'mode-input': 'multi',
    'mode-output': 'text',
    'mode-context': 'yes',
    'mode-framework': 'langchain',
    'mode-tools': 'get',
    'mode-reset': 'now',
    'mode-os': 'windows'
}

# Preset 2: Production Mode
presetProduction = {
    'mode-llm': 'globalChatgpt02',
    'mode-conversation': 'wakeUp',
    'mode-input': 'text',
    'mode-output': 'speech',
    'mode-context': 'yes',
    'mode-framework': 'fabric',
    'mode-tools': 'update',
    'mode-reset': 'now',
    'mode-os': 'windows'
}

# Preset 3: Testing Mode
presetTesting = {
    'mode-llm': 'local',
    'mode-conversation': 'sleep',
    'mode-input': 'file',
    'mode-output': 'text',
    'mode-context': 'no',
    'mode-framework': 'langchain',
    'mode-tools': 'get',
    'mode-reset': 'now',
    'mode-os': 'windows'
}

PRESETS = {
    'development': presetDevelopment,
    'production': presetProduction,
    'testing': presetTesting,
}

