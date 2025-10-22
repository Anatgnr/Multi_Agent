from crewai import Agent, Task, Process, Crew, LLM
from MCP.Files_editor import FilesSystemMCP
from MCP.WrapperMCP import MCPTool

def build_crew(prompt, agents_config, tasks_config):
    """
    Construit un Crew avec des agents et des tâches.
    Chaque agent peut utiliser un modèle Ollama différent défini dans agents_config.
    """
    agents = []
    tasks = []
    mcp_instance = FilesSystemMCP(base_path="Workspace")
    # MCPTool is a pydantic model-like tool; instantiate with keyword args
    mcp_tool = MCPTool(mcp=mcp_instance)

    for name, agent_data in agents_config.items():
        if not agent_data.get("enabled", True):
            continue

        # Chaque agent a son propre modèle Ollama (fallback sur llama3.2)
        model_name = agent_data.get("model", "llama3.2")
        llm = LLM(model=f"ollama/{model_name}", base_url="http://127.0.0.1:11434")

        agent = Agent(
            name=name,
            role=agent_data["role"],
            goal=agent_data["goal"],
            backstory=agent_data.get("backstory", ""),
            llm=llm,
            tools=[mcp_tool],
            verbose=True
        )

        # Récupération de la tâche correspondant à l'agent
        task_data = tasks_config.get(name) or next(
            (t for t in tasks_config.values() if t.get("agent","").lower() == name.lower()), None
        )
        if not task_data:
            print(f"⚠️ Aucune tâche trouvée pour l'agent '{name}' — ignoré.")
            continue

        description = task_data["description"].format(prompt=prompt)
        task = Task(
            agent=agent,
            description=description,
            expected_output=task_data.get("expected_output", ""),
            output_file=task_data.get("output_file")
        )

        agents.append(agent)
        tasks.append(task)

    # Crew final
    return Crew(
        agents=agents,
        tasks=tasks,
        model=None,              # Chaque agent gère son modèle
        process=Process.sequential,
        planning=False,
        cache=True,
        verbose=True
    )
