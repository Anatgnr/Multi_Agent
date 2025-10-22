### Gather the agents in the crew

from Agents.windows_app_maker import create_windows_app_maker
from crewai import Crew, Task, Agent
from Agents.architect import create_architect
from Agents.backend import create_backend_dev
from Agents.doc_writer import create_doc_writer
from Agents.dependency_manager import create_dependency_manager

def build_crew(prompt, agents_config, tasks_config, llm, mcp):
    architect = create_architect(llm=llm, mcp_tool=mcp)
    backend = create_backend_dev(llm=llm, mcp_tool=mcp)
    app_maker = create_windows_app_maker(llm=llm, mcp_tool=mcp)
    docwriter = create_doc_writer(llm=llm, mcp_tool=mcp)
    dependency_manager = create_dependency_manager(llm=llm, mcp_tool=mcp)

    agents = [architect, backend, app_maker, docwriter, dependency_manager]

    task_arch = Task(
        agent=architect,
        description=tasks_config["architecture"]["description"].format(prompt=prompt),
        expected_output=tasks_config["architecture"].get("expected_output", ""),
        output_file=tasks_config["architecture"].get("output_file")
    )
    task_backend = Task(
        agent=backend,
        description=tasks_config["backend"]["description"].format(prompt=prompt),
        expected_output=tasks_config["backend"].get("expected_output", ""),
        output_file=tasks_config["backend"].get("output_file")
    )
    task_app = Task(
        agent=app_maker,
        description=tasks_config["app"]["description"].format(prompt=prompt),
        expected_output=tasks_config["app"].get("expected_output", ""),
        output_file=tasks_config["app"].get("output_file")
    )
    task_doc = Task(
        agent=docwriter,
        description=tasks_config["doc"]["description"].format(prompt=prompt),
        expected_output=tasks_config["doc"].get("expected_output", ""),
        output_file=tasks_config["doc"].get("output_file")
    )
    task_dep = Task(
        agent=dependency_manager,
        description=tasks_config["dep"]["description"].format(prompt=prompt),
        expected_output=tasks_config["dep"].get("expected_output", ""),
        output_file=tasks_config["dep"].get("output_file")
    )

    tasks = [task_arch, task_backend, task_app, task_doc, task_dep]

    for name, data in agents_config.items():
        if data.get("enabled", True):
            agent = Agent(
                name=name,
                role=data["role"],
                goal=data["goal"],
                backstory=data.get("backstory", ""),
                llm=llm,
                mcp_tool=mcp
            )
            task = Task(
                agent=agent,
                description=data["task_template"].format(prompt=prompt),
                expected_output=data.get("expected_output", ""),
                output_file=data.get("output_file")
            )
            agents.append(agent)
            tasks.append(task)

    return Crew(agents=agents, tasks=tasks)
