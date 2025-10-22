from crewai import Agent

def create_windows_app_maker(llm=None, mcp_tool=None):
    return Agent(
        name="Windows_App_Maker",
        role="Windows Application Developer",
        goal="Create a Windows application based on user requirements.",
        backstory="You are an expert in Windows application development and UI design.",
        llm=llm,
        mcp_tool=mcp_tool
    )