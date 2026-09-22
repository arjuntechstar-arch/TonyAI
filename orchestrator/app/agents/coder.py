from .base_agent import BaseAgent
class CoderAgent(BaseAgent):
    name = "coder"
    def system_prompt(self):
        return """You are the coding agent for a local AI engineer.
Produce production-oriented code, preserve conventions, inspect before editing, and avoid destructive actions."""
