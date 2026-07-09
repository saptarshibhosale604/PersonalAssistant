#!/usr/bin/env python3
"""
Terminal Interface (Numbered / Conversational) - Mode Configuration Manager
-----------------------------------------------------------------------------
A lightweight, plain-text terminal application for navigating and managing
LLM configuration modes through a simple "modesTUI asks / Human answers by number"
workflow (instead of vim-style j/k/l/h navigation).

Flow:
  modesTUI:  select the mode:
       1. mode-llm             [local-1b]
       2. mode-stream          [false]
       ...
       11. [preset] development
       12. [preset] production
       13. [preset] testing
       14. [reset] reset to default
  Human: <number>

  If a mode was picked, the modesTUI then asks for the value:
  modesTUI: select mode value
      1 local        model running locally, jarvis like personality
      2 local-buddy  model running locally with best bud personality
      3 global       model running on cloud / chatgpt
  Human: <number>

  modesTUI:
  The value saved succesfully
  mode-llm: global

Author: Data Engineer
Date: 2025
Version: 6.0.0 (numbered/conversational edition)
"""

import os
import sys
import json
from typing import Dict, List, Any, Optional

# from UI.config import modeConfigFilePath, modeConfigSandboxFilePath, modeSandboxLocal, defaultConfig, modeConfigInitializationJson, presetDevelopment, presetProduction, presetTesting, PRESETS
from UI.config import *

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


# ============================================================================
# CONVERSATIONAL / NUMBERED UI
# ============================================================================

class ConversationalUIManager:
    """
    Drives the modesTUI/Human numbered-selection conversation:

        modesTUI: select the mode:
        1. mode-llm             [local-1b]
        ...
        Human:
        <number>

        modesTUI: select mode value
        1 local  ...
        Human:
        <number>

        modesTUI:
        The value saved succesfully
        mode-llm: global
    """

    def __init__(self, menuConfig: MenuConfig):
        self.menuConfig = menuConfig
        self.modeKeys = self.menuConfig.GetModeKeys()
        self.presetNames = list(PRESETS.keys())  # ['development', 'production', 'testing']
        # Build the ordered list of main-menu entries.
        # entries: ('mode', key) | ('preset', name) | ('reset', None)
        self.mainMenuEntries: List[tuple] = []
        for key in self.modeKeys:
            self.mainMenuEntries.append(('mode', key))
        for name in self.presetNames:
            self.mainMenuEntries.append(('preset', name))
        self.mainMenuEntries.append(('reset', None))
        self.isRunning = False

    # -------------------------------------------------------------- helpers
    @staticmethod
    def _Print(text: str = "") -> None:
        print(text)

    def _ReadHumanSelection(self, validCount: int) -> Optional[int]:
        """Print the 'Human:' prompt, read a number, validate it (1..validCount)."""
        self._Print("Human:")
        try:
            rawInput = input().strip()
        except (EOFError, KeyboardInterrupt):
            return None
        if rawInput.lower() in ("q", "quit", "exit"):
            return None
        if not rawInput.isdigit():
            self._Print(f"modesTUI: '{rawInput}' is not a valid number, please try again.")
            return self._ReadHumanSelection(validCount)
        choice = int(rawInput)
        if choice < 1 or choice > validCount:
            self._Print(f"modesTUI: please enter a number between 1 and {validCount}.")
            return self._ReadHumanSelection(validCount)
        return choice

    # ---------------------------------------------------------- main menu
    def RenderMainMenu(self) -> None:
        self._Print("modesTUI: select the mode:")
        self._Print("")
        for index, entry in enumerate(self.mainMenuEntries, start=1):
            entryType, payload = entry
            if entryType == 'mode':
                currentValue = self.menuConfig.GetCurrentValue(payload)
                self._Print(f"{index}. {payload:<20} [{currentValue}]")
            elif entryType == 'preset':
                self._Print(f"{index}. [preset] {payload}")
            elif entryType == 'reset':
                self._Print(f"{index}. [reset] reset to default")

    # ----------------------------------------------------------- sub menu
    def RenderSubMenu(self, modeKey: str) -> List[str]:
        """Prints the sub-menu for a mode and returns the ordered list of option keys."""
        self._Print("modesTUI: select mode value")
        subOptions = self.menuConfig.GetSubOptions(modeKey) or {}
        optionKeys = list(subOptions.keys())
        for index, optionKey in enumerate(optionKeys, start=1):
            description = subOptions[optionKey]
            self._Print(f"{index} {optionKey:<20} {description}")
        return optionKeys

    # -------------------------------------------------------------- flow
    def HandleModeSelection(self, modeKey: str) -> None:
        optionKeys = self.RenderSubMenu(modeKey)
        if not optionKeys:
            self._Print(f"modesTUI: mode '{modeKey}' has no selectable values.")
            return
        choice = self._ReadHumanSelection(len(optionKeys))
        if choice is None:
            self.isRunning = False
            return
        selectedValue = optionKeys[choice - 1]
        if self.menuConfig.SetCurrentValue(modeKey, selectedValue):
            self.menuConfig.SaveConfigToFile("mode_config.json")
            self._Print("modesTUI:")
            self._Print("The value saved succesfully")
            self._Print(f"{modeKey}: {selectedValue}")
        else:
            self._Print(f"modesTUI: could not save value for '{modeKey}'.")

    def HandlePresetSelection(self, presetName: str) -> None:
        presetConfig = PRESETS[presetName]
        if self.menuConfig.ApplyPreset(presetConfig):
            self.menuConfig.SaveConfigToFile("mode_config.json")
            self._Print("modesTUI:")
            self._Print("The value saved succesfully")
            for modeKey, value in presetConfig.items():
                self._Print(f"{modeKey}: {value}")
        else:
            self._Print(f"modesTUI: could not apply preset '{presetName}'.")

    def HandleResetSelection(self) -> None:
        if self.menuConfig.ResetToDefault():
            self.menuConfig.SaveConfigToFile("mode_config.json")
            self._Print("modesTUI:")
            self._Print("The value saved succesfully")
            currentConfig = self.menuConfig.GetCurrentConfiguration()
            for modeKey, value in currentConfig.items():
                self._Print(f"{modeKey}: {value}")
        else:
            self._Print("modesTUI: could not reset configuration.")

    # --------------------------------------------------------------- run
    def Run(self) -> None:
        self.isRunning = True
        while self.isRunning:
            self.RenderMainMenu()
            choice = self._ReadHumanSelection(len(self.mainMenuEntries))
            if choice is None:
                self._Print("modesTUI: Goodbye!")
                self.isRunning = False
                break

            entryType, payload = self.mainMenuEntries[choice - 1]
            if entryType == 'mode':
                self.HandleModeSelection(payload)
            elif entryType == 'preset':
                self.HandlePresetSelection(payload)
            elif entryType == 'reset':
                self.HandleResetSelection()

            self._Print("")

def ShowHelp() -> None:
    """
    Prints usage instructions for the numbered-selection TUI.
    Call this any time, e.g. from Run() before the main loop, or
    add a '?' check in _ReadHumanSelection to trigger it on demand.
    """
    print("AI: HOW TO USE THIS TUI")
    print("=" * 50)
    print()
    print("- At every 'Human:' prompt, type the NUMBER shown next to")
    print("  the option you want, then press Enter.")
    print()
    print("- Main menu numbers select a mode, a preset, or reset.")
    print("  Example: typing '1' opens the 'mode-llm' value list.")
    print()
    print("- Sub-menu numbers select the actual value for that mode.")
    print("  Example: typing '3' sets mode-llm to 'global'.")
    print()
    print("- After a value is set, it's saved automatically and you'll")
    print("  see: 'The value saved succesfully' followed by the change.")
    print()
    print("- You'll then return to the main menu to make more changes.")
    print()
    print("HOW TO EXIT:")
    print("  Type 'q', 'quit', or 'exit' at any 'Human:' prompt,")
    print("  or press Ctrl+C, and the AI will say 'Goodbye!' and stop.")
    print("=" * 50)

def Main(modeSandbox: str = "false") -> None:
    """Main entry point for the conversational, numbered-selection UI."""
    try:
        global modeConfigFilePath
        global modeConfigSandboxFilePath
        global modeSandboxLocal
        if modeSandbox == "true":
            modeSandboxLocal = modeSandbox
            modeConfigFilePath = modeConfigSandboxFilePath

        ShowHelp()
        loadedConfig = LoadConfigurationFromFile("mode_config.json")
        initializedConfig = InitializeConfigWithLoadedValues(modeConfigInitializationJson, loadedConfig)
        menuConfig = MenuConfig(initializedConfig)

        uiManager = ConversationalUIManager(menuConfig)
        uiManager.Run()
    except KeyboardInterrupt:
        print("\n\nApplication terminated by user.")
        sys.exit(0)
    except Exception as error:
        print(f"Fatal error: {str(error)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    Main()