import os, json

class FilesSystemMCP:
    """
    MCP Local class to manage file operations in a specified directory.
    """
    
    def __init__(self, base_path="./workspace"):
        # Ensure the base path exists
        self.base_path = os.path.abspath(base_path)
        os.makedirs(self.base_path, exist_ok=True)
        
    def _safe_path(self, path):
        # Prevent directory traversal attacks
        full_path = os.path.abspath(os.path.join(self.base_path, path))
        if not full_path.startswith(self.base_path):
            raise ValueError("Attempted directory traversal detected.")
        return full_path
    
    def list_files(self, path=""):
        abs_path = self._safe_path(path)
        return os.listdir(abs_path)
    
    def read_file(self, path):
        abs_path = self._safe_path(path)
        with open(abs_path, 'r') as file:
            return file.read()
        
    def write_file(self, path, content):
        abs_path = self._safe_path(path)
        with open(abs_path, 'w') as file:
            file.write(content)
        return f"File '{path}' written successfully."
    
    def handle_request(self, request_json):
        # Execute a request in JSON format
        request = json.loads(request_json)
        action = request.get("action")
        args = request.get("args", {})

        if action == "list_files":
            return json.dumps(self.list_files(**args))
        elif action == "read_file":
            return json.dumps(self.read_file(**args))
        elif action == "write_file":
            return self.write_file(**args)
        else:
            return json.dumps({"error": "Unknown action"})