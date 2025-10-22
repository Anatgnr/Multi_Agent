# orchestrator.py
import yaml
from Agents.crew import build_crew
from MCP.Files_editor import FilesSystemMCP
from LLM.local_model import load_llm
from LLM.local_provider import LocalLLM

class Orchestrator:
    def __init__(self):
        # Charge les configurations YAML
        with open("Config/agents.yaml", "r") as f:
            self.agents_config = yaml.safe_load(f)

        with open("Config/tasks.yaml", "r") as f:
            self.tasks_config = yaml.safe_load(f)

        # Initialise les outils MCP (ex : FileSystem)
        self.mcp_files = FilesSystemMCP(base_path="Workspace")
        
        # Initialise le LLM local pour les agents and wrap it into a provider object
        raw_llm = load_llm()
        self.llm = LocalLLM(raw_llm)

    def run(self, user_prompt: str):
        """
        Point d'entrée principal de l'orchestration.
        """
        print(f"\n🧭 Lancement du Crew pour le prompt : {user_prompt}\n")

        # Création du crew avec les agents et leurs tâches
        crew = build_crew(
            prompt=user_prompt,
            agents_config=self.agents_config,
            tasks_config=self.tasks_config,
            mcp=self.mcp_files,
            llm=self.llm
        )

        # Lancement de la collaboration
        try:
            result = crew.kickoff()
        except Exception as e:
            print("⚠️  creAI kickoff failed, falling back to simple sequential execution:\n", e)
            # Fallback: run tasks sequentially by calling each agent's llm directly
            outputs = {}
            for task in getattr(crew, "tasks", []):
                agent = getattr(task, "agent", None)
                desc = getattr(task, "description", "")
                out_file = getattr(task, "output_file", None)

                # Try to get an llm callable from the agent
                llm_obj = getattr(agent, "llm", None)
                text = None
                try:
                    if llm_obj is None:
                        raise RuntimeError("No llm attached to agent")

                    # If llm_obj has a .call method, use it
                    if hasattr(llm_obj, "call") and callable(llm_obj.call):
                        resp = llm_obj.call(desc)
                        # resp may be dict-like or string
                        if isinstance(resp, dict) and "output" in resp:
                            text = resp["output"]
                        elif isinstance(resp, dict) and "generated_text" in resp:
                            text = resp["generated_text"]
                        else:
                            text = str(resp)
                    elif callable(llm_obj):
                        text = str(llm_obj(desc))
                    else:
                        raise RuntimeError("Agent llm is not callable")
                except Exception as ex:
                    text = f"[ERROR] failed to run agent {getattr(agent,'name',repr(agent))}: {ex}"

                outputs[getattr(task, "output_file", f"task_{id(task)}.txt")] = text

                # write to mcp if possible
                if out_file and hasattr(self.mcp_files, "create_file"):
                    try:
                        self.mcp_files.create_file(out_file, text)
                        print(f"Wrote fallback output to {out_file}")
                    except Exception as write_ex:
                        print(f"Failed to write {out_file}: {write_ex}")

            # simple aggregation of outputs
            result = "\n\n".join([f"{k}:\n{v}" for k, v in outputs.items()])

        # Sauvegarde le résultat dans le Workspace
        self.mcp_files.write_file("result.txt", result)
        print("\n✅ Résultat sauvegardé dans Workspace/result.txt")

        return result
