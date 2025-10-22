from crewai import Agent

def create_doc_writer(llm=None, mcp_tool=None):
    return Agent(
        name="DocWriter",
        role="Rédacteur technique",
        goal="Rédiger le README du projet généré.",
        backstory="Vous êtes un expert en rédaction technique et en documentation.",
        llm=llm,
        mcp_tool=mcp_tool
    )
