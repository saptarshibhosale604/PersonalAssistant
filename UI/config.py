
modeConfigFilePath = "./UI/modesConfig.json"
modeConfigSandboxFilePath = "./UI/modesConfigSandbox.json"
modeSandboxLocal = "false"

# Create file with default configuration
defaultConfig = {
    'mode-llm': 'local-1b',
    'mode-stream': 'false',
    'mode-conversation': 'wakeUp',
    'mode-input': 'text',
    'mode-output': 'text',
    'mode-context': 'yes',
    'mode-framework': 'langchain',
    'mode-sandbox': 'false',
    'mode-tools': 'update',
    'mode-reset': 'now'
}

modeConfigInitializationJson = {
    'mode-llm': {
        'current': 'local',
        'allowed': {
            'local': 'Model running locally, Jarvis like personality',
            'local-4b': 'Model running locally, qwen3.5:4b',
            'local-4b-no-tools': 'Model running locally, qwen3.5:4b, without any agent tools',
            'local-buddy': 'Model running locally with Best bud personality',
            'global': 'Model running on cloud / chatgpt'
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
    'mode-reset': 'now'
}

# Preset 2: Production Mode
presetProduction = {
    'mode-llm': 'global',
    'mode-conversation': 'wakeUp',
    'mode-input': 'text',
    'mode-output': 'speech',
    'mode-context': 'yes',
    'mode-framework': 'fabric',
    'mode-tools': 'update',
    'mode-reset': 'now'
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
    'mode-reset': 'now'
}

PRESETS = {
    'development': presetDevelopment,
    'production': presetProduction,
    'testing': presetTesting,
}

