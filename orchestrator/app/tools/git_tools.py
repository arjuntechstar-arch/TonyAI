import subprocess
from .workspace import Workspace
class GitTools:
    def __init__(self): self.workspace = Workspace()
    def status(self):
        return subprocess.run(["git","status","--short"], cwd=self.workspace.root, capture_output=True, text=True).stdout
    def diff(self):
        return subprocess.run(["git","diff","--"], cwd=self.workspace.root, capture_output=True, text=True).stdout
