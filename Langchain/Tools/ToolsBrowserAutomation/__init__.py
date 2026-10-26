from Langchain.Tools.ToolsBrowserAutomation.toolsGoogleForms import InspectActiveGoogleForm, FillGoogleForm

def ToolsList() -> list:
    return [
        InspectActiveGoogleForm,
        FillGoogleForm
    ]
