from crewai import Agent

def create_architect(llm=None, mcp_tool=None):
    return Agent(
        name="Architect",
        role="Architecte system",
        goal="Define the structure of the app based on user needs.",
        backstory="You are an expert in distributed systems and AI.",
        llm=llm,
        mcp_tool=mcp_tool
    )
