from crewai import Agent

def create_Docker_agent(llm=None, mcp_tool=None):
    return Agent(
        name="Docker",
        role="Docker Expert",
        goal="Manage containerization and deployment of the application.",
        backstory="You are an expert in Docker and container orchestration.",
        llm=llm,
        mcp_tool=mcp_tool
    )
