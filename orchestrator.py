import yaml
from Agents.crew import build_crew
from MCP.Files_editor import FilesSystemMCP

class Orchestrator:
    def __init__(self):
        # Chargement des configs YAML
        with open("Config/agents.yaml", "r") as f:
            self.agents_config = yaml.safe_load(f)

        with open("Config/tasks.yaml", "r") as f:
            self.tasks_config = yaml.safe_load(f)

        # Outils MCP
        self.mcp_files = FilesSystemMCP(base_path="Workspace")

    def run(self, user_prompt: str):
        print(f"\n🧭 Lancement du Crew pour le prompt : {user_prompt}\n")

        # Création du crew
        crew = build_crew(
            prompt=user_prompt,
            agents_config=self.agents_config,
            tasks_config=self.tasks_config,
        )

        # Exécution
        try:
            result = crew.kickoff()  # Chaque agent utilise son modèle Ollama
        except Exception as e:
            print("⚠️  Échec du kickoff, fallback séquentiel :", e)
            # Fallback séquentiel
            outputs = {}
            for task in getattr(crew, "tasks", []):
                agent = getattr(task, "agent", None)
                desc = getattr(task, "description", "")
                out_file = getattr(task, "output_file", None)

                text = None
                try:
                    llm_obj = getattr(agent, "llm", None)
                    if not llm_obj:
                        raise RuntimeError("Pas de LLM attaché à l'agent")

                    # Appel du LLM
                    if hasattr(llm_obj, "call") and callable(llm_obj.call):
                        resp = llm_obj.call(desc)
                        if isinstance(resp, dict) and "output" in resp:
                            text = resp["output"]
                        else:
                            text = str(resp)
                    elif callable(llm_obj):
                        text = str(llm_obj(desc))
                    else:
                        raise RuntimeError("LLM non callable")
                except Exception as ex:
                    text = f"[ERROR] {getattr(agent,'name','unknown')}: {ex}"

                outputs[out_file or f"task_{id(task)}.txt"] = text

                # Écriture via MCP
                if out_file and hasattr(self.mcp_files, "create_file"):
                    try:
                        self.mcp_files.create_file(out_file, text)
                        print(f"Wrote fallback output to {out_file}")
                    except Exception as write_ex:
                        print(f"Failed to write {out_file}: {write_ex}")

            # Agrégation des résultats
            result = "\n\n".join([f"{k}:\n{v}" for k,v in outputs.items()])

        # Sauvegarde finale: ensure we write a string/serializable object
        try:
            write_result = self.mcp_files.write_file("result.txt", result)
            print("\n✅ Résultat sauvegardé dans Workspace/result.txt")
            # Small debug: show the type of result written
            print(f"(debug) result type: {type(result)}")
        except Exception as ex:
            print(f"Failed to write result.txt: {ex}")
            # As a fallback, serialize and try again
            try:
                import json
                serialized = json.dumps(result, default=str, indent=2)
            except Exception:
                serialized = str(result)
            self.mcp_files.write_file("result.txt", serialized)
            print("\n✅ Résultat (serialized) sauvegardé dans Workspace/result.txt")
        return result
