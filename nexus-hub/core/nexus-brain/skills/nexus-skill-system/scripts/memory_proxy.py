import os
import json
import logging
from datetime import datetime

# Nexus Memory Proxy - Core logic for NMP
# Bu script, Gemini CLI ve Ollama/WebUI arasındaki hafıza köprüsüdür.

class NexusMemory:
    def __init__(self, memory_path="/DATA/projects/agentops-nexus/data/memory.json"):
        self.memory_path = memory_path
        self.log = logging.getLogger("NexusMemory")
        self._ensure_memory_exists()

    def _ensure_memory_exists(self):
        if not os.path.exists(self.memory_path):
            os.makedirs(os.path.dirname(self.memory_path), exist_ok=True)
            with open(self.memory_path, 'w') as f:
                json.dump({"LT": {}, "PM": {}, "ST": {}}, f)

    def save_fact(self, key, value, category="PM"):
        """Bir gerçeği (fact) hafızaya kaydet."""
        with open(self.memory_path, 'r+') as f:
            data = json.load(f)
            data[category][key] = {
                "value": value,
                "timestamp": datetime.utcnow().isoformat(),
                "source": "NexusBrain"
            }
            f.seek(0)
            json.dump(data, f, indent=4)
            f.truncate()
        return True

    def get_context(self):
        """Mevcut tüm hafızayı 'context' olarak döndür."""
        with open(self.memory_path, 'r') as f:
            return json.load(f)

if __name__ == "__main__":
    memory = NexusMemory()
    # Test
    memory.save_fact("SystemStatus", "Active and Synced", "ST")
    print("Memory Synced.")
