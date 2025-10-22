from crewai import Agent

def create_backend_dev(llm=None, mcp_tool=None):
    return Agent(
        name="Backend_Dev",
        role="Backend Developer",
        goal="Implement the logic and APIs of the application.",
        backstory="You are an expert in backend development and databases.",
        llm=llm,
        mcp_tool=mcp_tool
    )