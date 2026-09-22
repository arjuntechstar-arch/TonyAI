import subprocess
from .workspace import Workspace
class ShellTools:
    ALLOWED_PREFIXES = ("dotnet build", "dotnet test", "dotnet run", "python", "npm test", "npm run build")
    def __init__(self): self.workspace = Workspace()
    def run(self, command: str, approved=False):
        if not approved: raise PermissionError("Shell execution requires approval")
        if not command.startswith(self.ALLOWED_PREFIXES): raise PermissionError("Command is not on allow-list")
        r = subprocess.run(command, cwd=self.workspace.root, shell=True, capture_output=True, text=True, timeout=300)
        return {"returncode": r.returncode, "stdout": r.stdout[-12000:], "stderr": r.stderr[-12000:]}
