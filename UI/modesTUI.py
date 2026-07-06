#!/usr/bin/env python3
"""
Terminal Graphical Interface (TGI) - Mode Configuration Manager

A lightweight terminal user interface (TUI) application for navigating and managing
LLM configuration modes with vim-style keyboard navigation, preset configurations,
and reset functionality. Supports persistent configuration loading/saving.

Author: Data Engineer
Date: 2025
Version: 5.1.0
"""

import os
import sys
import json
from typing import Dict, List, Any, Optional


# ============================================================================
# DEFAULT CONFIGURATION AND PRESETS
# ============================================================================
# modeConfigFilePath = "mode_config.json"
# modeConfigFilePath = "/root/ProjectRpi/Rpi/PersonalAssistant/Langchain/Tools/toolsConfig.json"
# modeConfigFilePath = "/root/ProjectRpi/Rpi/PersonalAssistant/Langchain/Tools/modesConfig.json"
# modeConfigFilePath = "/home/ssbrpi/ProjectRpi/Rpi/PersonalAssistant/Langchain/Tools/modesConfig.json"
modeConfigFilePath = "/root/ProjectRpi/Rpi/PersonalAssistant/UI/modesConfig.json"
modeConfigSandboxFilePath = "/root/ProjectRpi/Rpi/PersonalAssistant/UI/modesConfigSandbox.json"
modeSandboxLocal = "false"
# Create file with default configuration
defaultConfig = {
    'mode-llm': 'local-1b',
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
#             "local-1b" :
#             "llama3.2:1b" :
#             "local-3b" :
#             "local-7b-raw" :
#             "local-7b-vision" :
#                 llava:7b                8dd30f6b0cb1    4.7 GB    10 days ago     
# gemma3:4b               a2af6cc3eb7f    3.3 GB    10 days ago     
# llama2-uncensored:7b    44040b922233    3.8 GB    10 days ago     
# llama3.2:latest         a80c4f17acd5    2.0 GB    2 months ago    
# llama3.2:1b             baf6a787fdff    1.3 GB    2 months ago    
#
            'local-buddy': 'Model running locally with Best bud personality',
            'global': 'Model running on cloud / chatgpt'
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
            'multiline': 'Text input mode multiline'
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
    'mode-input': 'multiline',
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


# ============================================================================
# UTILITY FUNCTIONS FOR FILE MANAGEMENT
# ============================================================================

def LoadConfigurationFromFile(filename: str = "mode_config.json", modeSandbox: str = "false") -> Dict[str, str]:
    """
    Load configuration from file. If file doesn't exist, create it with default values.
    
    Args:
        filename: Name of the configuration file
        
    Returns:
        Dictionary containing configuration values
    """
    try:
        global modeConfigFilePath
        global modeConfigSandboxFilePath

        # print(f"load_modes: modeSandbox: {modeSandbox}")

        # Load configuration from file (or create it if doesn't exist)
        if modeSandbox == "true":
           modeConfigFilePath = modeConfigSandboxFilePath

        filename = modeConfigFilePath

        # print(f"modeConfigFilePath modesTUI LoadConfigurationFromFile filename: {filename}")

        if os.path.exists(filename):
            with open(filename, 'r') as file:
                return json.load(file)
        else:
            global defaultConfig

            with open(filename, 'w') as file:
                json.dump(defaultConfig, file, indent=2)
            return defaultConfig
    except Exception as error:
        print(f"Error loading configuration: {str(error)}")
        return {
            'mode-llm': 'local',
            'mode-conversation': 'wakeUp',
            'mode-input': 'text',
            'mode-output': 'text',
            'mode-context': 'yes',
            'mode-framework': 'langchain',
            'mode-tools': 'update',
            'mode-reset': 'now'
        }


def InitializeConfigWithLoadedValues(baseConfig: Dict[str, Any], loadedValues: Dict[str, str]) -> Dict[str, Any]:
    """
    Initialize base configuration with loaded values from file.
    
    Args:
        baseConfig: Base configuration structure
        loadedValues: Loaded configuration values from file
        
    Returns:
        Updated configuration dictionary
    """
    try:
        updatedConfig = json.loads(json.dumps(baseConfig))
        for modeKey, value in loadedValues.items():
            if modeKey in updatedConfig:
                updatedConfig[modeKey]['current'] = value
        return updatedConfig
    except Exception as error:
        print(f"Error initializing configuration: {str(error)}")
        return baseConfig


class Color:
    """ANSI color codes for terminal output."""
    
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    
    # Colors
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    
    # Bright colors
    BRIGHT_GREEN = "\033[92m"
    BRIGHT_CYAN = "\033[96m"
    BRIGHT_YELLOW = "\033[93m"


class MenuConfig:
    """Manages menu configuration."""
    
    def __init__(self, modeConfigInitializationJson: Dict[str, Any]):
        """
        Initialize MenuConfig with mode configuration.
        
        Args:
            modeConfigInitializationJson: Dictionary containing mode configurations
            
        Raises:
            ValueError: If configuration is invalid
        """
        try:
            if not isinstance(modeConfigInitializationJson, dict) or not modeConfigInitializationJson:
                raise ValueError("Configuration must be a non-empty dictionary")
            
            self.modeConfig = modeConfigInitializationJson
            self.modeKeys = list(self.modeConfig.keys())
            self.defaultConfig = self._GetDeepCopy(modeConfigInitializationJson)
            
        except Exception as error:
            raise ValueError(f"Failed to initialize MenuConfig: {str(error)}")
    
    @staticmethod
    def _GetDeepCopy(configDict: Dict[str, Any]) -> Dict[str, Any]:
        """Create a deep copy of the configuration."""
        return json.loads(json.dumps(configDict))
    
    def GetModeKeys(self) -> List[str]:
        """Get all available mode keys."""
        return self.modeKeys.copy()
    
    def GetModeConfig(self, modeKey: str) -> Optional[Dict[str, Any]]:
        """Get configuration for a specific mode."""
        return self.modeConfig.get(modeKey)
    
    def GetSubOptions(self, modeKey: str) -> Optional[Dict[str, str]]:
        """Get sub-options for a mode."""
        try:
            modeData = self.GetModeConfig(modeKey)
            if modeData and "allowed" in modeData:
                return modeData["allowed"].copy()
            return None
        except Exception as error:
            print(f"{Color.RED}Error retrieving sub-options: {str(error)}{Color.RESET}")
            return None
    
    def GetCurrentValue(self, modeKey: str) -> Optional[str]:
        """Get the current value of a mode."""
        try:
            modeData = self.GetModeConfig(modeKey)
            if modeData and "current" in modeData:
                return modeData["current"]
            return None
        except Exception as error:
            print(f"{Color.RED}Error getting current value: {str(error)}{Color.RESET}")
            return None
    
    def SetCurrentValue(self, modeKey: str, value: str) -> bool:
        """Set the current value of a mode."""
        try:
            if modeKey not in self.modeConfig:
                raise ValueError(f"Mode key '{modeKey}' not found")
            
            allowedValues = self.modeConfig[modeKey].get("allowed", {})
            if value not in allowedValues:
                raise ValueError(f"Value '{value}' not allowed for mode '{modeKey}'")
            
            self.modeConfig[modeKey]["current"] = value
            return True
        except Exception as error:
            print(f"{Color.RED}Error setting current value: {str(error)}{Color.RESET}")
            return False
    
    def GetCurrentConfiguration(self) -> Dict[str, str]:
        """Get current configuration as a simple dictionary."""
        result = {}
        for modeKey in self.modeKeys:
            result[modeKey] = self.GetCurrentValue(modeKey)
        return result
    
    def ApplyPreset(self, presetConfig: Dict[str, str]) -> bool:
        """
        Apply a preset configuration.
        
        Args:
            presetConfig: Dictionary containing preset values
            
        Returns:
            True if successful, False otherwise
        """
        try:
            for modeKey, value in presetConfig.items():
                if not self.SetCurrentValue(modeKey, value):
                    return False
            return True
        except Exception as error:
            print(f"{Color.RED}Error applying preset: {str(error)}{Color.RESET}")
            return False
    
    def ResetToDefault(self) -> bool:
        """
        Reset configuration to default values.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            self.modeConfig = self._GetDeepCopy(self.defaultConfig)

            global modeConfigFilePath
            if os.path.exists(modeConfigFilePath):
                os.remove(modeConfigFilePath)
                print(f"File '{modeConfigFilePath}' has been deleted successfully.")
            else:
                print(f"File '{modeConfigFilePath}' does not exist.")

            return True
        except Exception as error:
            print(f"{Color.RED}Error resetting configuration: {str(error)}{Color.RESET}")
            return False
    
    def SaveConfigToFile(self, filename: str = "mode_config.json") -> bool:
        """
        Save current configuration to a JSON file.
        
        Args:
            filename: Name of the file to save configuration to
            
        Returns:
            True if successful, False otherwise
        """
        try:
            global modeConfigFilePath

            # Load configuration from file (or create it if doesn't exist)
            if modeSandboxLocal == "true":
                modeConfigFilePath = modeConfigSandboxFilePath

            filename = modeConfigFilePath

            currentConfig = self.GetCurrentConfiguration()
            with open(filename, 'w') as file:
                json.dump(currentConfig, file, indent=2)
            return True
        except Exception as error:
            print(f"{Color.RED}Error saving configuration: {str(error)}{Color.RESET}")
            return False


class TerminalRenderer:
    """Handles terminal rendering."""
    
    @staticmethod
    def ClearScreen() -> None:
        """Clear the terminal screen."""
        os.system("clear" if os.name == "posix" else "cls")
    
    @staticmethod
    def PrintColored(text: str, color: str = Color.WHITE, bold: bool = False) -> None:
        """Print colored text to terminal."""
        style = f"{Color.BOLD}" if bold else ""
        print(f"{style}{color}{text}{Color.RESET}")


class OptionNavigator:
    """Manages selection within a menu."""
    
    def __init__(self, options: List[str]):
        """Initialize OptionNavigator with a list of options."""
        try:
            if not options:
                raise ValueError("Options list cannot be empty")
            self.options = options
            self.selectedIndex = 0
        except Exception as error:
            print(f"Error initializing OptionNavigator: {str(error)}")
            self.options = []
            self.selectedIndex = 0
    
    def MoveUp(self) -> None:
        """Move selection up (k key)."""
        if self.selectedIndex > 0:
            self.selectedIndex -= 1
        else:
            self.selectedIndex = len(self.options) - 1
    
    def MoveDown(self) -> None:
        """Move selection down (j key)."""
        if self.selectedIndex < len(self.options) - 1:
            self.selectedIndex += 1
        else:
            self.selectedIndex = 0
    
    def GetSelectedOption(self) -> str:
        """Get the currently selected option."""
        if 0 <= self.selectedIndex < len(self.options):
            return self.options[self.selectedIndex]
        return ""
    
    def SetSelectedIndex(self, index: int) -> None:
        """Set the selected index directly."""
        if 0 <= index < len(self.options):
            self.selectedIndex = index
    
    def GetSelectedIndex(self) -> int:
        """Get the current selected index."""
        return self.selectedIndex


class NavigationManager:
    """Manages navigation state and history."""
    
    def __init__(self, menuConfig: MenuConfig):
        """Initialize NavigationManager."""
        self.menuConfig = menuConfig
        self.navigationStack: List[Optional[str]] = [None]
        self.currentIndex = 0
    
    def PushState(self, modeKey: Optional[str]) -> None:
        """Push a new state onto the navigation stack."""
        try:
            self.navigationStack.append(modeKey)
            self.currentIndex = len(self.navigationStack) - 1
        except Exception as error:
            print(f"Error pushing navigation state: {str(error)}")
    
    def PopState(self) -> Optional[str]:
        """Pop the current state and return to previous."""
        try:
            if len(self.navigationStack) > 1:
                self.navigationStack.pop()
                self.currentIndex = len(self.navigationStack) - 1
            return self.GetCurrentState()
        except Exception as error:
            print(f"Error popping navigation state: {str(error)}")
            return None
    
    def GetCurrentState(self) -> Optional[str]:
        """Get the current navigation state."""
        if 0 <= self.currentIndex < len(self.navigationStack):
            return self.navigationStack[self.currentIndex]
        return None
    
    def IsAtMainMenu(self) -> bool:
        """Check if currently at main menu."""
        return self.GetCurrentState() is None


class TerminalUIManager:
    """Main Terminal UI Manager."""
    
    def __init__(self, modeConfigInitializationJson: Dict[str, Any]):
        """Initialize the Terminal UI Manager."""
        try:
            self.menuConfig = MenuConfig(modeConfigInitializationJson)
            self.renderer = TerminalRenderer()
            self.navigationManager = NavigationManager(self.menuConfig)
            
            # Main menu options: modes + presets + reset
            mainMenuOptions = self.menuConfig.GetModeKeys() + ["[PRESET] Development", "[PRESET] Production", "[PRESET] Testing", "[RESET] Reset to Default"]
            self.modeNavigator = OptionNavigator(mainMenuOptions)
            self.subOptionNavigator: Optional[OptionNavigator] = None
            self.currentPreset: Optional[str] = None
            self.currentSelectedMode: Optional[str] = None
            self.isRunning = False
            self.isEditMode = False
            
        except Exception as error:
            raise ValueError(f"Failed to initialize TerminalUIManager: {str(error)}")
    
    def RenderMainMenu(self) -> None:
        """Render the main menu with all available modes and presets."""
        try:
            self.renderer.ClearScreen()
            
            # Header
            self.renderer.PrintColored("┌─ MODE CONFIGURATION MANAGER ─────────────────────┐", Color.CYAN, bold=True)
            self.renderer.PrintColored("│", Color.CYAN)
            
            mainOptions = self.modeNavigator.options
            selectedIndex = self.modeNavigator.GetSelectedIndex()
            
            for index, option in enumerate(mainOptions):
                if "[PRESET]" in option:
                    # Preset option
                    if index == selectedIndex:
                        indicator = "▶"
                        self.renderer.PrintColored(f"  {indicator} {option:<45}", Color.BRIGHT_GREEN, bold=True)
                    else:
                        indicator = " "
                        self.renderer.PrintColored(f"  {indicator} {option:<45}", Color.BRIGHT_CYAN)
                elif "[RESET]" in option:
                    # Reset option
                    if index == selectedIndex:
                        indicator = "▶"
                        self.renderer.PrintColored(f"  {indicator} {option:<45}", Color.BRIGHT_GREEN, bold=True)
                    else:
                        indicator = " "
                        self.renderer.PrintColored(f"  {indicator} {option:<45}", Color.BRIGHT_CYAN)
                else:
                    # Regular mode option
                    currentValue = self.menuConfig.GetCurrentValue(option)
                    if index == selectedIndex:
                        indicator = "▶"
                        line = f"  {indicator} {option:<30} [{currentValue}]"
                        self.renderer.PrintColored(line, Color.BRIGHT_GREEN, bold=True)
                    else:
                        indicator = " "
                        line = f"  {indicator} {option:<30} [{currentValue}]"
                        self.renderer.PrintColored(line, Color.BRIGHT_CYAN)
            
            self.renderer.PrintColored("│", Color.CYAN)
            self.renderer.PrintColored("└─────────────────────────────────────────────────────┘", Color.CYAN)
            print()
            self.renderer.PrintColored("vim keys: [j]down [k]up [l]select [h]back [q]quit", Color.YELLOW)
            
        except Exception as error:
            self.renderer.PrintColored(f"Error rendering main menu: {str(error)}", Color.RED)
    
    def RenderSubMenu(self, selectedMode: str) -> None:
        """Render sub-menu for a selected mode."""
        try:
            self.renderer.ClearScreen()
            
            # Header
            self.renderer.PrintColored(f"┌─ {selectedMode.upper()} ─────────────────────────────────┐", Color.CYAN, bold=True)
            self.renderer.PrintColored("│", Color.CYAN)
            
            subOptions = self.menuConfig.GetSubOptions(selectedMode)
            currentValue = self.menuConfig.GetCurrentValue(selectedMode)
            
            if subOptions:
                optionKeys = list(subOptions.keys())
                selectedIndex = self.subOptionNavigator.GetSelectedIndex() if self.subOptionNavigator else 0
                
                for index, optionKey in enumerate(optionKeys):
                    optionDesc = subOptions[optionKey]
                    
                    if index == selectedIndex:
                        indicator = "▶"
                        isActive = optionKey == currentValue
                        status = "[ACTIVE]" if isActive else ""
                        line = f"  {indicator} {optionKey:<20} {status:<10} {optionDesc}"
                        self.renderer.PrintColored(line, Color.BRIGHT_GREEN, bold=True)
                    else:
                        indicator = " "
                        isActive = optionKey == currentValue
                        status = "[ACTIVE]" if isActive else ""
                        line = f"  {indicator} {optionKey:<20} {status:<10} {optionDesc}"
                        self.renderer.PrintColored(line, Color.BRIGHT_CYAN)
            
            self.renderer.PrintColored("│", Color.CYAN)
            self.renderer.PrintColored("└──────────────────────────────────────────────────────┘", Color.CYAN)
            print()
            
            if self.isEditMode:
                self.renderer.PrintColored("vim keys: [j]down [k]up [space]select [l]save [h]back [q]quit", Color.YELLOW)
            else:
                self.renderer.PrintColored("vim keys: [j]down [k]up [l]select [h]back [q]quit", Color.YELLOW)
        
        except Exception as error:
            self.renderer.PrintColored(f"Error rendering sub-menu: {str(error)}", Color.RED)
    
    def RenderPresetMenu(self, presetName: str, presetConfig: Dict[str, str]) -> None:
        """Render preset configuration display."""
        try:
            self.renderer.ClearScreen()
            
            # Header
            self.renderer.PrintColored(f"┌─ PRESET: {presetName.upper()} ──────────────────────────────┐", Color.CYAN, bold=True)
            self.renderer.PrintColored("│", Color.CYAN)
            
            for modeKey, value in presetConfig.items():
                line = f"  {modeKey:<30} → {value}"
                self.renderer.PrintColored(line, Color.BRIGHT_CYAN)
            
            self.renderer.PrintColored("│", Color.CYAN)
            self.renderer.PrintColored("└──────────────────────────────────────────────────────┘", Color.CYAN)
            print()
            self.renderer.PrintColored("Press [l] to apply preset | [h] to go back", Color.YELLOW)
        
        except Exception as error:
            self.renderer.PrintColored(f"Error rendering preset menu: {str(error)}", Color.RED)
    
    def HandleMainMenuInput(self, userInput: str) -> None:
        """Handle user input when on main menu."""
        try:
            if userInput in ["j", "J"]:
                self.modeNavigator.MoveDown()
            elif userInput in ["k", "K"]:
                self.modeNavigator.MoveUp()
            elif userInput in ["l", "L"]:
                selectedOption = self.modeNavigator.GetSelectedOption()
                
                if "[PRESET] Development" in selectedOption:
                    self.currentPreset = "Development"
                    self.navigationManager.PushState("preset_development")
                elif "[PRESET] Production" in selectedOption:
                    self.currentPreset = "Production"
                    self.navigationManager.PushState("preset_production")
                elif "[PRESET] Testing" in selectedOption:
                    self.currentPreset = "Testing"
                    self.navigationManager.PushState("preset_testing")
                elif "[RESET]" in selectedOption:
                    self.navigationManager.PushState("reset_menu")
                else:
                    # Regular mode
                    self.isEditMode = False
                    self.currentSelectedMode = selectedOption
                    self.navigationManager.PushState(selectedOption)
                    self._InitializeSubMenu(selectedOption)
            elif userInput in ["h", "H"]:
                self._ExitWithoutSave()
            elif userInput in ["q", "Q"]:
                self._ExitWithoutSave()
            else:
                self._ShowHelp()
        except Exception as error:
            self.renderer.PrintColored(f"Error handling input: {str(error)}", Color.RED)
    
    def HandleSubMenuInput(self, userInput: str, selectedMode: str) -> None:
        """Handle user input when on sub-menu."""
        try:
            if userInput in ["j", "J"]:
                if self.subOptionNavigator:
                    self.subOptionNavigator.MoveDown()
            elif userInput in ["k", "K"]:
                if self.subOptionNavigator:
                    self.subOptionNavigator.MoveUp()
            elif userInput in ["l", "L"]:
                # In edit mode: save and exit
                # Not in edit mode: select option and exit
                if self.subOptionNavigator:
                    selectedOption = self.subOptionNavigator.GetSelectedOption()
                    if self.menuConfig.SetCurrentValue(selectedMode, selectedOption):
                        self._ExitWithSave()
            elif userInput == " ":
                # Space key - select option and enter edit mode
                if self.subOptionNavigator:
                    selectedOption = self.subOptionNavigator.GetSelectedOption()
                    if self.menuConfig.SetCurrentValue(selectedMode, selectedOption):
                        self.isEditMode = True
            elif userInput in ["h", "H"]:
                if self.isEditMode:
                    # In edit mode, h goes back to navigate between modes
                    self.isEditMode = False
                    self.navigationManager.PopState()
                else:
                    # Not in edit mode, h goes back normally
                    self.navigationManager.PopState()
            elif userInput in ["q", "Q"]:
                self._ExitWithoutSave()
        except Exception as error:
            self.renderer.PrintColored(f"Error handling input: {str(error)}", Color.RED)
    
    def HandlePresetInput(self, userInput: str) -> None:
        """Handle user input when viewing a preset."""
        try:
            if userInput in ["l", "L"]:
                # Apply preset
                if self.currentPreset == "Development":
                    self.menuConfig.ApplyPreset(presetDevelopment)
                elif self.currentPreset == "Production":
                    self.menuConfig.ApplyPreset(presetProduction)
                elif self.currentPreset == "Testing":
                    self.menuConfig.ApplyPreset(presetTesting)
                self._ExitWithSave()
            elif userInput in ["h", "H"]:
                self.navigationManager.PopState()
            elif userInput in ["q", "Q"]:
                self._ExitWithoutSave()
        except Exception as error:
            self.renderer.PrintColored(f"Error handling preset input: {str(error)}", Color.RED)
    
    def HandleResetInput(self, userInput: str) -> None:
        """Handle user input when on reset menu."""
        try:
            if userInput in ["l", "L"]:
                # Reset to default and go back to main menu with success message
                if self.menuConfig.ResetToDefault():
                    # self.navigationManager.PopState()
                    # self.isEditMode = False
                    self._ShowResetSuccessMessage()
                    # self._ExitWithSave()
                    self._ExitWithoutSave()
            elif userInput in ["h", "H"]:
                self.navigationManager.PopState()
            elif userInput in ["q", "Q"]:
                self._ExitWithoutSave()
        except Exception as error:
            self.renderer.PrintColored(f"Error handling reset input: {str(error)}", Color.RED)
    
    def _InitializeSubMenu(self, modeKey: str) -> None:
        """Initialize the sub-menu for a selected mode."""
        try:
            subOptions = self.menuConfig.GetSubOptions(modeKey)
            if subOptions:
                optionKeys = list(subOptions.keys())
                self.subOptionNavigator = OptionNavigator(optionKeys)
                
                # Set selected index to current value
                currentValue = self.menuConfig.GetCurrentValue(modeKey)
                if currentValue in optionKeys:
                    currentIndex = optionKeys.index(currentValue)
                    self.subOptionNavigator.SetSelectedIndex(currentIndex)
        except Exception as error:
            self.renderer.PrintColored(f"Error initializing sub-menu: {str(error)}", Color.RED)
    
    def _ShowResetSuccessMessage(self) -> None:
        """Show reset success message and allow user to continue."""
        try:
            self.renderer.ClearScreen()
            self.renderer.PrintColored("", Color.GREEN)
            self.renderer.PrintColored("╔════════════════════════════════════════════════════╗", Color.GREEN, bold=True)
            self.renderer.PrintColored("║                                                    ║", Color.GREEN, bold=True)
            self.renderer.PrintColored("║  ✓ Configuration reset to default successfully!   ║", Color.GREEN, bold=True)
            self.renderer.PrintColored("║                                                    ║", Color.GREEN, bold=True)
            self.renderer.PrintColored("╚════════════════════════════════════════════════════╝", Color.GREEN, bold=True)
            print()
            
            # Display default configuration
            self.renderer.PrintColored("Default Configuration:", Color.YELLOW, bold=True)
            currentConfig = self.menuConfig.GetCurrentConfiguration()
            for key, value in currentConfig.items():
                self.renderer.PrintColored(f"  {key:<30} → {value}", Color.BRIGHT_CYAN)
            
            print()
            self.renderer.PrintColored("Press any key to continue...", Color.BRIGHT_GREEN, bold=True)
            input()
        
        except Exception as error:
            self.renderer.PrintColored(f"Error: {str(error)}", Color.RED)
    
    def _ExitWithSave(self) -> None:
        """Save configuration and exit with success message."""
        try:
            self.renderer.ClearScreen()
            self.renderer.PrintColored("", Color.GREEN)
            self.renderer.PrintColored("╔════════════════════════════════════════════════════╗", Color.GREEN, bold=True)
            self.renderer.PrintColored("║                                                    ║", Color.GREEN, bold=True)
            self.renderer.PrintColored("║  ✓ Configuration saved successfully!               ║", Color.GREEN, bold=True)
            self.renderer.PrintColored("║                                                    ║", Color.GREEN, bold=True)
            self.renderer.PrintColored("╚════════════════════════════════════════════════════╝", Color.GREEN, bold=True)
            print()
            
            # Save to file
            if self.menuConfig.SaveConfigToFile("mode_config.json"):
                self.renderer.PrintColored("File saved: modeConfig.json", Color.BRIGHT_GREEN, bold=True)
                print()
                
                # Display current configuration
                self.renderer.PrintColored("Current Configuration:", Color.YELLOW, bold=True)
                currentConfig = self.menuConfig.GetCurrentConfiguration()
                for key, value in currentConfig.items():
                    self.renderer.PrintColored(f"  {key:<30} → {value}", Color.BRIGHT_CYAN)
            else:
                self.renderer.PrintColored("Warning: Could not save to file", Color.YELLOW)
            
            print()
            self.renderer.PrintColored("Exiting...", Color.BRIGHT_GREEN, bold=True)
            self.isRunning = False
        
        except Exception as error:
            self.renderer.PrintColored(f"Error: {str(error)}", Color.RED)
            self.isRunning = False
    
    def _ExitWithoutSave(self) -> None:
        """Exit without saving."""
        try:
            self.renderer.ClearScreen()
            self.renderer.PrintColored("", Color.YELLOW)
            self.renderer.PrintColored("╔════════════════════════════════════════════════════╗", Color.YELLOW, bold=True)
            self.renderer.PrintColored("║                                                    ║", Color.YELLOW, bold=True)
            self.renderer.PrintColored("║  ⚠ Exiting without saving configuration           ║", Color.YELLOW, bold=True)
            self.renderer.PrintColored("║                                                    ║", Color.YELLOW, bold=True)
            self.renderer.PrintColored("╚════════════════════════════════════════════════════╝", Color.YELLOW, bold=True)
            print()
            self.renderer.PrintColored("Goodbye!", Color.BRIGHT_YELLOW, bold=True)
            self.isRunning = False
        
        except Exception as error:
            self.renderer.PrintColored(f"Error: {str(error)}", Color.RED)
            self.isRunning = False
    
    def _ShowHelp(self) -> None:
        """Display help information."""
        try:
            self.renderer.ClearScreen()
            self.renderer.PrintColored("╔═ KEYBOARD SHORTCUTS ══════════════════════════╗", Color.CYAN, bold=True)
            self.renderer.PrintColored("║", Color.CYAN)
            self.renderer.PrintColored("║  Navigation:", Color.YELLOW, bold=True)
            self.renderer.PrintColored("║    [j] - Move down     [k] - Move up", Color.CYAN)
            self.renderer.PrintColored("║    [l] - Select/Enter  [h] - Go back", Color.CYAN)
            self.renderer.PrintColored("║", Color.CYAN)
            self.renderer.PrintColored("║  Edit Mode:", Color.YELLOW, bold=True)
            self.renderer.PrintColored("║    [space] - Select option (enter edit mode)", Color.CYAN)
            self.renderer.PrintColored("║    [l] - Save and exit", Color.CYAN)
            self.renderer.PrintColored("║    [h] - Go back without saving", Color.CYAN)
            self.renderer.PrintColored("║", Color.CYAN)
            self.renderer.PrintColored("║  Actions:", Color.YELLOW, bold=True)
            self.renderer.PrintColored("║    [q] - Quit application", Color.CYAN)
            self.renderer.PrintColored("║", Color.CYAN)
            self.renderer.PrintColored("╚═════════════════════════════════════════════════╝", Color.CYAN, bold=True)
            print()
            self.renderer.PrintColored("Press any key to return...", Color.BRIGHT_YELLOW, bold=True)
            input()
        
        except Exception as error:
            self.renderer.PrintColored(f"Error displaying help: {str(error)}", Color.RED)
    
    def _GetUserInput(self) -> str:
        """Get single character input from user."""
        try:
            import tty
            import termios
            
            fd = sys.stdin.fileno()
            oldSettings = termios.tcgetattr(fd)
            try:
                tty.setraw(fd)
                ch = sys.stdin.read(1)
                return ch
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, oldSettings)
        except (ImportError, Exception):
            # Fallback for Windows
            userInput = input()
            return userInput[0] if userInput else ""
    
    def Run(self) -> None:
        """Main run loop for the Terminal UI."""
        try:
            self.isRunning = True
            
            while self.isRunning:
                currentState = self.navigationManager.GetCurrentState()
                
                if currentState is None:
                    self.RenderMainMenu()
                elif currentState == "preset_development":
                    self.RenderPresetMenu("Development", presetDevelopment)
                elif currentState == "preset_production":
                    self.RenderPresetMenu("Production", presetProduction)
                elif currentState == "preset_testing":
                    self.RenderPresetMenu("Testing", presetTesting)
                elif currentState == "reset_menu":
                    self.renderer.ClearScreen()
                    self.renderer.PrintColored("┌─ RESET TO DEFAULT ────────────────────────────────┐", Color.CYAN, bold=True)
                    self.renderer.PrintColored("│", Color.CYAN)
                    self.renderer.PrintColored("  All modes will be reset to their default values", Color.BRIGHT_CYAN)
                    self.renderer.PrintColored("│", Color.CYAN)
                    self.renderer.PrintColored("└──────────────────────────────────────────────────────┘", Color.CYAN)
                    print()
                    self.renderer.PrintColored("Press [l] to reset | [h] to cancel | [q] to quit", Color.YELLOW)
                else:
                    self.RenderSubMenu(currentState)
                
                try:
                    userInput = self._GetUserInput()
                    
                    if currentState is None:
                        self.HandleMainMenuInput(userInput)
                    elif currentState in ["preset_development", "preset_production", "preset_testing"]:
                        self.HandlePresetInput(userInput)
                    elif currentState == "reset_menu":
                        self.HandleResetInput(userInput)
                    else:
                        self.HandleSubMenuInput(userInput, currentState)
                
                except KeyboardInterrupt:
                    self._ExitWithoutSave()
                
                except Exception as error:
                    self.renderer.PrintColored(f"Error: {str(error)}", Color.RED)
            
        except Exception as error:
            print(f"Critical error in main loop: {str(error)}")
            sys.exit(1)


def Main(modeSandbox: str = "false") -> None:
    """Main entry point for the Terminal UI application."""
    try:
        global modeConfigFilePath
        global modeConfigSandboxFilePath
        global modeSandboxLocal

        # Load configuration from file (or create it if doesn't exist)
        if modeSandbox == "true":
            modeSandboxLocal = modeSandbox
            modeConfigFilePath = modeConfigSandboxFilePath

        loadedConfig = LoadConfigurationFromFile("mode_config.json")
        
        # Initialize configuration with loaded values
        initializedConfig = InitializeConfigWithLoadedValues(modeConfigInitializationJson, loadedConfig)
        
        # Start the TUI
        tuiManager = TerminalUIManager(initializedConfig)
        tuiManager.Run()
    
    except KeyboardInterrupt:
        print("\n\nApplication terminated by user.")
        sys.exit(0)
    except Exception as error:
        print(f"Fatal error: {str(error)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    Main()


