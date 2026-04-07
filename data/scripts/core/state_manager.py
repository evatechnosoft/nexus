import json
import os

class AgentStateManager:
    """Ajan durumunu kalıcı hale getiren (checkpoint) yönetici sınıf."""
    
    def __init__(self, state_file="agent_state.json"):
        self.state_file = state_file
        self.state = self.load_state()

    def load_state(self):
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}

    def save_checkpoint(self, current_task, findings, token_usage):
        """Kritik bilgileri dosyaya mühürler."""
        self.state = {
            "last_task": current_task,
            "knowledge_graph": findings,
            "token_usage_stats": token_usage,
            "timestamp": os.path.getmtime(self.state_file) if os.path.exists(self.state_file) else 0
        }
        with open(self.state_file, 'w', encoding='utf-8') as f:
            json.dump(self.state, f, indent=4, ensure_ascii=False)
        return True

    def get_token_report(self):
        """Dashboard için token raporu üretir."""
        usage = self.state.get("token_usage_stats", {"current": 0, "limit": 128000})
        percent = (usage["current"] / usage["limit"]) * 100
        bar_length = 20
        filled = int(percent / (100 / bar_length))
        bar = "█" * filled + "░" * (bar_length - filled)
        
        return {
            "percent": percent,
            "bar": bar,
            "current": usage["current"],
            "limit": usage["limit"]
        }

# Örnek Kullanım
if __name__ == "__main__":
    manager = AgentStateManager()
    # Simüle edilmiş veri
    manager.save_checkpoint(
        "Advanced Agent Research", 
        ["Unix-style tools", "SubAgent isolation", "State persistence"],
        {"current": 24500, "limit": 128000}
    )
    report = manager.get_token_report()
    print(f"Token Usage: {report['percent']:.1f}% [{report['bar']}] {report['current']}/{report['limit']}")
