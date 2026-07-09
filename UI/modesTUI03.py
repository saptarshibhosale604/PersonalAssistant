#!/usr/bin/env python3
"""
Terminal Interface (Plain) - Mode Configuration Manager

A lightweight, plain-text terminal application for navigating and managing
LLM configuration modes with vim-style keyboard navigation, preset configurations,
and reset functionality. Supports persistent configuration loading/saving.

No colors, no box-drawing characters - just plain text output, so it works
reliably in any terminal, log file, or non-interactive shell.

Author: Data Engineer
Date: 2025
Version: 5.1.0 (plain-text edition)
"""

import os
import sys
import json
from typing import Dict, List, Any, Optional


# ============================================================================
# DEFAULT CONFIGURATION AND PRESETS
# ============================================================================
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
    """
    try:
        global modeConfigFilePath
        global modeConfigSandboxFilePath

        if modeSandbox == "true":
            modeConfigFilePath = modeConfigSandboxFilePath

        filename = modeConfigFilePath

        if os.path.exists(filename):
            with open(filename, 'r') as file:
                return json.load(file)
        else:
            global defaultConfig
            os.makedirs(os.path.dirname(filename) or ".", exist_ok=True)
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


class MenuConfig:
    """Manages menu configuration."""

    def __init__(self, modeConfigInitializationJson: Dict[str, Any]):
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
        return json.loads(json.dumps(configDict))

    def GetModeKeys(self) -> List[str]:
        return self.modeKeys.copy()

    def GetModeConfig(self, modeKey: str) -> Optional[Dict[str, Any]]:
        return self.modeConfig.get(modeKey)

    def GetSubOptions(self, modeKey: str) -> Optional[Dict[str, str]]:
        try:
            modeData = self.GetModeConfig(modeKey)
            if modeData and "allowed" in modeData:
                return modeData["allowed"].copy()
            return None
        except Exception as error:
            print(f"Error retrieving sub-options: {str(error)}")
            return None

    def GetCurrentValue(self, modeKey: str) -> Optional[str]:
        try:
            modeData = self.GetModeConfig(modeKey)
            if modeData and "current" in modeData:
                return modeData["current"]
            return None
        except Exception as error:
            print(f"Error getting current value: {str(error)}")
            return None

    def SetCurrentValue(self, modeKey: str, value: str) -> bool:
        try:
            if modeKey not in self.modeConfig:
                raise ValueError(f"Mode key '{modeKey}' not found")

            allowedValues = self.modeConfig[modeKey].get("allowed", {})
            if value not in allowedValues:
                raise ValueError(f"Value '{value}' not allowed for mode '{modeKey}'")

            self.modeConfig[modeKey]["current"] = value
            return True
        except Exception as error:
            print(f"Error setting current value: {str(error)}")
            return False

    def GetCurrentConfiguration(self) -> Dict[str, str]:
        result = {}
        for modeKey in self.modeKeys:
            result[modeKey] = self.GetCurrentValue(modeKey)
        return result

    def ApplyPreset(self, presetConfig: Dict[str, str]) -> bool:
        try:
            for modeKey, value in presetConfig.items():
                if not self.SetCurrentValue(modeKey, value):
                    return False
            return True
        except Exception as error:
            print(f"Error applying preset: {str(error)}")
            return False

    def ResetToDefault(self) -> bool:
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
            print(f"Error resetting configuration: {str(error)}")
            return False

    def SaveConfigToFile(self, filename: str = "mode_config.json") -> bool:
        try:
            global modeConfigFilePath

            if modeSandboxLocal == "true":
                modeConfigFilePath = modeConfigSandboxFilePath

            filename = modeConfigFilePath

            currentConfig = self.GetCurrentConfiguration()
            os.makedirs(os.path.dirname(filename) or ".", exist_ok=True)
            with open(filename, 'w') as file:
                json.dump(currentConfig, file, indent=2)
            return True
        except Exception as error:
            print(f"Error saving configuration: {str(error)}")
            return False


class TerminalRenderer:
    """Handles plain terminal rendering (no colors, no box drawing)."""

    @staticmethod
    def ClearScreen() -> None:
        os.system("clear" if os.name == "posix" else "cls")

    @staticmethod
    def Print(text: str = "") -> None:
        print(text)


class OptionNavigator:
    """Manages selection within a menu."""

    def __init__(self, options: List[str]):
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
        if self.selectedIndex > 0:
            self.selectedIndex -= 1
        else:
            self.selectedIndex = len(self.options) - 1

    def MoveDown(self) -> None:
        if self.selectedIndex < len(self.options) - 1:
            self.selectedIndex += 1
        else:
            self.selectedIndex = 0

    def GetSelectedOption(self) -> str:
        if 0 <= self.selectedIndex < len(self.options):
            return self.options[self.selectedIndex]
        return ""

    def SetSelectedIndex(self, index: int) -> None:
        if 0 <= index < len(self.options):
            self.selectedIndex = index

    def GetSelectedIndex(self) -> int:
        return self.selectedIndex


class NavigationManager:
    """Manages navigation state and history."""

    def __init__(self, menuConfig: MenuConfig):
        self.menuConfig = menuConfig
        self.navigationStack: List[Optional[str]] = [None]
        self.currentIndex = 0

    def PushState(self, modeKey: Optional[str]) -> None:
        try:
            self.navigationStack.append(modeKey)
            self.currentIndex = len(self.navigationStack) - 1
        except Exception as error:
            print(f"Error pushing navigation state: {str(error)}")

    def PopState(self) -> Optional[str]:
        try:
            if len(self.navigationStack) > 1:
                self.navigationStack.pop()
                self.currentIndex = len(self.navigationStack) - 1
            return self.GetCurrentState()
        except Exception as error:
            print(f"Error popping navigation state: {str(error)}")
            return None

    def GetCurrentState(self) -> Optional[str]:
        if 0 <= self.currentIndex < len(self.navigationStack):
            return self.navigationStack[self.currentIndex]
        return None

    def IsAtMainMenu(self) -> bool:
        return self.GetCurrentState() is None


class TerminalUIManager:
    """Main Terminal UI Manager (plain text, no colors)."""

    def __init__(self, modeConfigInitializationJson: Dict[str, Any]):
        try:
            self.menuConfig = MenuConfig(modeConfigInitializationJson)
            self.renderer = TerminalRenderer()
            self.navigationManager = NavigationManager(self.menuConfig)

            mainMenuOptions = self.menuConfig.GetModeKeys() + [
                "[PRESET] Development",
                "[PRESET] Production",
                "[PRESET] Testing",
                "[RESET] Reset to Default"
            ]
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
            self.renderer.Print("MODE CONFIGURATION MANAGER")
            self.renderer.Print("=" * 50)
            self.renderer.Print()

            mainOptions = self.modeNavigator.options
            selectedIndex = self.modeNavigator.GetSelectedIndex()

            for index, option in enumerate(mainOptions):
                marker = ">" if index == selectedIndex else " "

                if "[PRESET]" in option or "[RESET]" in option:
                    self.renderer.Print(f"{marker} {option}")
                else:
                    currentValue = self.menuConfig.GetCurrentValue(option)
                    self.renderer.Print(f"{marker} {option:<20} [{currentValue}]")

            self.renderer.Print()
            self.renderer.Print("=" * 50)
            self.renderer.Print("keys: j=down k=up l=select h=back q=quit  (? for help)")

        except Exception as error:
            self.renderer.Print(f"Error rendering main menu: {str(error)}")

    def RenderSubMenu(self, selectedMode: str) -> None:
        """Render sub-menu for a selected mode."""
        try:
            self.renderer.ClearScreen()
            self.renderer.Print(selectedMode.upper())
            self.renderer.Print("=" * 50)
            self.renderer.Print()

            subOptions = self.menuConfig.GetSubOptions(selectedMode)
            currentValue = self.menuConfig.GetCurrentValue(selectedMode)

            if subOptions:
                optionKeys = list(subOptions.keys())
                selectedIndex = self.subOptionNavigator.GetSelectedIndex() if self.subOptionNavigator else 0

                for index, optionKey in enumerate(optionKeys):
                    optionDesc = subOptions[optionKey]
                    marker = ">" if index == selectedIndex else " "
                    isActive = optionKey == currentValue
                    status = "[ACTIVE]" if isActive else ""
                    self.renderer.Print(f"{marker} {optionKey:<15} {status:<10} {optionDesc}")

            self.renderer.Print()
            self.renderer.Print("=" * 50)
            if self.isEditMode:
                self.renderer.Print("keys: j=down k=up space=select l=save h=back q=quit")
            else:
                self.renderer.Print("keys: j=down k=up l=select h=back q=quit")

        except Exception as error:
            self.renderer.Print(f"Error rendering sub-menu: {str(error)}")

    def RenderPresetMenu(self, presetName: str, presetConfig: Dict[str, str]) -> None:
        """Render preset configuration display."""
        try:
            self.renderer.ClearScreen()
            self.renderer.Print(f"PRESET: {presetName.upper()}")
            self.renderer.Print("=" * 50)
            self.renderer.Print()

            for modeKey, value in presetConfig.items():
                self.renderer.Print(f"  {modeKey:<20} -> {value}")

            self.renderer.Print()
            self.renderer.Print("=" * 50)
            self.renderer.Print("keys: l=apply preset  h=back  q=quit")

        except Exception as error:
            self.renderer.Print(f"Error rendering preset menu: {str(error)}")

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
                    self.isEditMode = False
                    self.currentSelectedMode = selectedOption
                    self.navigationManager.PushState(selectedOption)
                    self._InitializeSubMenu(selectedOption)
            elif userInput in ["h", "H"]:
                self._ExitWithoutSave()
            elif userInput in ["q", "Q"]:
                self._ExitWithoutSave()
            elif userInput == "?":
                self._ShowHelp()
            else:
                self._ShowHelp()
        except Exception as error:
            self.renderer.Print(f"Error handling input: {str(error)}")

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
                if self.subOptionNavigator:
                    selectedOption = self.subOptionNavigator.GetSelectedOption()
                    if self.menuConfig.SetCurrentValue(selectedMode, selectedOption):
                        self._ExitWithSave()
            elif userInput == " ":
                if self.subOptionNavigator:
                    selectedOption = self.subOptionNavigator.GetSelectedOption()
                    if self.menuConfig.SetCurrentValue(selectedMode, selectedOption):
                        self.isEditMode = True
            elif userInput in ["h", "H"]:
                if self.isEditMode:
                    self.isEditMode = False
                    self.navigationManager.PopState()
                else:
                    self.navigationManager.PopState()
            elif userInput in ["q", "Q"]:
                self._ExitWithoutSave()
        except Exception as error:
            self.renderer.Print(f"Error handling input: {str(error)}")

    def HandlePresetInput(self, userInput: str) -> None:
        """Handle user input when viewing a preset."""
        try:
            if userInput in ["l", "L"]:
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
            self.renderer.Print(f"Error handling preset input: {str(error)}")

    def HandleResetInput(self, userInput: str) -> None:
        """Handle user input when on reset menu."""
        try:
            if userInput in ["l", "L"]:
                if self.menuConfig.ResetToDefault():
                    self._ShowResetSuccessMessage()
                    self._ExitWithoutSave()
            elif userInput in ["h", "H"]:
                self.navigationManager.PopState()
            elif userInput in ["q", "Q"]:
                self._ExitWithoutSave()
        except Exception as error:
            self.renderer.Print(f"Error handling reset input: {str(error)}")

    def _InitializeSubMenu(self, modeKey: str) -> None:
        """Initialize the sub-menu for a selected mode."""
        try:
            subOptions = self.menuConfig.GetSubOptions(modeKey)
            if subOptions:
                optionKeys = list(subOptions.keys())
                self.subOptionNavigator = OptionNavigator(optionKeys)

                currentValue = self.menuConfig.GetCurrentValue(modeKey)
                if currentValue in optionKeys:
                    currentIndex = optionKeys.index(currentValue)
                    self.subOptionNavigator.SetSelectedIndex(currentIndex)
        except Exception as error:
            self.renderer.Print(f"Error initializing sub-menu: {str(error)}")

    def _ShowResetSuccessMessage(self) -> None:
        """Show reset success message and allow user to continue."""
        try:
            self.renderer.ClearScreen()
            self.renderer.Print("Configuration reset to default successfully!")
            self.renderer.Print()

            self.renderer.Print("Default Configuration:")
            currentConfig = self.menuConfig.GetCurrentConfiguration()
            for key, value in currentConfig.items():
                self.renderer.Print(f"  {key:<20} -> {value}")

            self.renderer.Print()
            self.renderer.Print("Press Enter to continue...")
            input()

        except Exception as error:
            self.renderer.Print(f"Error: {str(error)}")

    def _ExitWithSave(self) -> None:
        """Save configuration and exit with success message."""
        try:
            self.renderer.ClearScreen()
            self.renderer.Print("Configuration saved successfully!")
            self.renderer.Print()

            if self.menuConfig.SaveConfigToFile("mode_config.json"):
                self.renderer.Print(f"File saved: {modeConfigFilePath}")
                self.renderer.Print()

                self.renderer.Print("Current Configuration:")
                currentConfig = self.menuConfig.GetCurrentConfiguration()
                for key, value in currentConfig.items():
                    self.renderer.Print(f"  {key:<20} -> {value}")
            else:
                self.renderer.Print("Warning: Could not save to file")

            self.renderer.Print()
            self.renderer.Print("Exiting...")
            self.isRunning = False

        except Exception as error:
            self.renderer.Print(f"Error: {str(error)}")
            self.isRunning = False

    def _ExitWithoutSave(self) -> None:
        """Exit without saving."""
        try:
            self.renderer.ClearScreen()
            self.renderer.Print("Exiting without saving configuration")
            self.renderer.Print("Goodbye!")
            self.isRunning = False

        except Exception as error:
            self.renderer.Print(f"Error: {str(error)}")
            self.isRunning = False

    def _ShowHelp(self) -> None:
        """Display help information."""
        try:
            self.renderer.ClearScreen()
            self.renderer.Print("KEYBOARD SHORTCUTS")
            self.renderer.Print("=" * 50)
            self.renderer.Print()
            self.renderer.Print("Navigation:")
            self.renderer.Print("  j - Move down     k - Move up")
            self.renderer.Print("  l - Select/Enter  h - Go back")
            self.renderer.Print()
            self.renderer.Print("Edit Mode:")
            self.renderer.Print("  space - Select option (enter edit mode)")
            self.renderer.Print("  l     - Save and exit")
            self.renderer.Print("  h     - Go back without saving")
            self.renderer.Print()
            self.renderer.Print("Actions:")
            self.renderer.Print("  q - Quit application")
            self.renderer.Print("  ? - Show this help")
            self.renderer.Print()
            self.renderer.Print("Press Enter to return...")
            input()

        except Exception as error:
            self.renderer.Print(f"Error displaying help: {str(error)}")

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
                    self.renderer.Print("RESET TO DEFAULT")
                    self.renderer.Print("=" * 50)
                    self.renderer.Print()
                    self.renderer.Print("All modes will be reset to their default values")
                    self.renderer.Print()
                    self.renderer.Print("=" * 50)
                    self.renderer.Print("keys: l=reset  h=cancel  q=quit")
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
                    self.renderer.Print(f"Error: {str(error)}")

        except Exception as error:
            print(f"Critical error in main loop: {str(error)}")
            sys.exit(1)


def Main(modeSandbox: str = "false") -> None:
    """Main entry point for the Terminal UI application."""
    try:
        global modeConfigFilePath
        global modeConfigSandboxFilePath
        global modeSandboxLocal

        if modeSandbox == "true":
            modeSandboxLocal = modeSandbox
            modeConfigFilePath = modeConfigSandboxFilePath

        loadedConfig = LoadConfigurationFromFile("mode_config.json")

        initializedConfig = InitializeConfigWithLoadedValues(modeConfigInitializationJson, loadedConfig)

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