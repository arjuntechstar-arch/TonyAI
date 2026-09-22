class BaseAgent:
    name = "base"
    def system_prompt(self) -> str:
        return "You are a careful local software engineering agent."

    async def run(self, client, model: str, task: str, context: str = ""):
        messages = [
            {"role": "system", "content": self.system_prompt()},
            {"role": "user", "content": f"TASK:\n{task}\n\nCONTEXT:\n{context}"},
        ]
        return await client.chat(model, messages, keep_alive=0)
