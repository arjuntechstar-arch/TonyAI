from .base_agent import BaseAgent
class ReviewerAgent(BaseAgent):
    name = "reviewer"
    def system_prompt(self):
        return """You are the code review agent. Review correctness, security, maintainability,
performance, error handling, tests, and architecture. Do not make changes."""
