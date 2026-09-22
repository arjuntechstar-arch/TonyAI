from .base_agent import BaseAgent
class DebuggerAgent(BaseAgent):
    name = "debugger"
    def system_prompt(self):
        return """You are the debugging agent. Use errors, stack traces, source context, and recent changes
 to identify likely causes and propose the smallest safe fix and verification command."""
