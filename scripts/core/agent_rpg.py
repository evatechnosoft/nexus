import json
import os
import time

class AgentRPGStats:
    """Ajan teknik verilerini RPG metriklerine (Stamina, Vitality, Strength) dönüştüren sınıf."""
    
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
        return {"token_usage_stats": {"current": 0, "limit": 128000}, "hallucination_rate": 0.05, "active_agents": 1}

    def calculate_rpg_stats(self):
        """Teknik verileri RPG metriklerine çevirir."""
        usage = self.state.get("token_usage_stats", {"current": 0, "limit": 128000})
        hallucination = self.state.get("hallucination_rate", 0.05)
        active_agents = self.state.get("active_agents", 1)

        # STAMINA: Token kullanımı arttıkça düşer.
        stamina_percent = 100 - (usage["current"] / usage["limit"] * 100)
        
        # LUCK: Halüsinasyon oranı arttıkça düşer.
        luck_percent = max(0, 100 - (hallucination * 1000)) # 0.1 -> %0 Luck
        
        # STRENGTH: Aktif ajan sayısı ve görev karmaşıklığı.
        strength = active_agents * 20
        
        # VITALITY: Sistem kararlılığı (Şu an sabit, ilerde hata loglarına göre değişebilir).
        vitality = 100 if stamina_percent > 20 else 50

        return {
            "STAMINA": {"val": stamina_percent, "icon": "⚡", "label": "Context Memory"},
            "VITALITY": {"val": vitality, "icon": "❤️", "label": "System Health"},
            "STRENGTH": {"val": strength, "icon": "💪", "label": "Processing Power"},
            "LUCK": {"val": luck_percent, "icon": "🍀", "label": "Reasoning Accuracy"},
        }

    def render_dashboard(self):
        """CLI üzerinden RPG kartı basar."""
        stats = self.calculate_rpg_stats()
        output = ["\n[ AGENT CHARACTER SHEET ]\n" + "="*40]
        
        for name, data in stats.items():
            bar_len = 20
            filled = int(data["val"] / (100 / bar_len))
            bar = "█" * filled + "░" * (bar_len - filled)
            status = " [RESTING]" if name == "STAMINA" and data["val"] < 20 else ""
            output.append(f"{data['icon']} {name:<10} [{bar}] {data['val']:>5.1f}% | {data['label']}{status}")
        
        output.append("="*40)
        return "\n".join(output)

if __name__ == "__main__":
    rpg = AgentRPGStats()
    # Simüle edilmiş durumu kaydet
    rpg.state["token_usage_stats"] = {"current": 35000, "limit": 128000}
    rpg.state["hallucination_rate"] = 0.02
    rpg.state["active_agents"] = 3
    
    print(rpg.render_dashboard())
