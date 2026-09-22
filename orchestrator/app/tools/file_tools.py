from .workspace import Workspace
class FileTools:
    def __init__(self): self.workspace = Workspace()
    def list_files(self, relative="."):
        root = self.workspace.safe_path(relative)
        return [str(p.relative_to(self.workspace.root)) for p in root.rglob("*") if p.is_file()][:500]
    def read_file(self, relative):
        return self.workspace.safe_path(relative).read_text(encoding="utf-8")
    def write_file(self, relative, content, approved=False):
        if not approved: raise PermissionError("Write requires approval")
        p = self.workspace.safe_path(relative); p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8"); return str(p)
