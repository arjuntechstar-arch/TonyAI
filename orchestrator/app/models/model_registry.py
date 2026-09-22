from pathlib import Path
import yaml

class ModelRegistry:
    def __init__(self):
        p = Path(__file__).resolve().parents[1] / "config" / "models.yaml"
        self.data = yaml.safe_load(p.read_text(encoding="utf-8"))

    def get(self, role: str) -> dict:
        item = self.data["models"].get(role)
        if not item:
            raise KeyError(f"Unknown model role: {role}")
        if item.get("enabled", True) is False:
            raise RuntimeError(f"Model role '{role}' is disabled")
        return item

    def all(self):
        return self.data["models"]
