from .base_agent import BaseAgent
class TesterAgent(BaseAgent):
    name = "tester"
    def system_prompt(self):
        return """You are the test agent. Define safe build/test checks, interpret failures,
and return actionable diagnostics."""
