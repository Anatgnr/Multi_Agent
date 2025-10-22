from typing import Type, Union, ClassVar
from pydantic import BaseModel, Field
from crewai.tools import BaseTool
from .Files_editor import FilesSystemMCP
import json
import os

class MCPToolInput(BaseModel):
    input: Union[str, dict] = Field(..., description="Instruction JSON ou texte brut à traiter par le MCP.")

class MCPTool(BaseTool):
    name: str = "FilesSystemMCP"
    description: str = "Tool to manage files in the workspace (description loaded dynamically)"
    args_schema: Type[BaseModel] = MCPToolInput

    def __init__(self, mcp: FilesSystemMCP, **kwargs):
            super().__init__(**kwargs)
            print("✅ MCPTool loaded")
            self._mcp = mcp  # On stocke le MCP réel ici
            # On change la description pour donner la bonne info aux agents
            description_path = os.path.join(os.path.dirname(__file__), "description.txt")
            if os.path.exists(description_path):
                with open(description_path, "r", encoding="utf-8") as f:
                    self.description = f.read()


    def _run(self, input: Union[str, dict]) -> str:
        """Exécute les actions sur le système de fichiers."""
        try:
            # Si on reçoit déjà un dict, inutile de reparser
            if isinstance(input, dict):
                request = input
            else:
                request = json.loads(input)

            action = request.get("action")
            args = request.get("args", {})

            if action == "list_files":
                return json.dumps(self._mcp.list_files(**args))
            elif action == "read_file":
                return self._mcp.read_file(**args)
            elif action == "write_file":
                return self._mcp.write_file(**args)
            elif action == "create_file":
                return self._mcp.create_file(**args)
            elif action == "create_structure":
                return self._mcp.create_structure(**args)
            else:
                return f"[MCPTool] Unknown action: {action}"
        except json.JSONDecodeError:
            # Si l’input n’est pas JSON, on le traite comme du texte à écrire
            return self._mcp.write_file("output.txt", input)
        except Exception as e:
            return f"[MCPTool] Error: {str(e)}"
