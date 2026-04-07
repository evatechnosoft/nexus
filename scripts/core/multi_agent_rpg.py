import json
import os
import time

class MultiAgentRPGManager:
    """Ajanların (Analist, Fetch, Design, vb.) RPG metriklerini, skillerini ve buff/debuff durumlarını yöneten gelişmiş sınıf."""
    
    def __init__(self, state_file="multi_agent_party_state.json"):
        self.state_file = state_file
        self.agents = self.load_state()

    def load_state(self):
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {}
        return {}

    def update_agent(self, name, role, tokens, errors=0, reasoning_effort=50, hallucination=0.02, skills=None, active_buffs=None):
        """Spesifik bir ajanın RPG metriklerini, yeteneklerini ve bufflarını günceller."""
        limit = 128000
        stamina = max(0, 100 - (tokens / limit * 100))
        vitality = max(0, 100 - (errors * 10))
        strength = reasoning_effort
        luck = max(0, 100 - (hallucination * 1000))

        # Otomatik Debuff: Fatigue (Yorgunluk)
        debuffs = []
        if stamina < 30:
            debuffs.append({"name": "FATIGUE", "icon": "😫", "effect": "-15% Processing Power"})
            strength *= 0.85
        if hallucination > 0.05:
            debuffs.append({"name": "CONFUSED", "icon": "😵", "effect": "Luck Penalty"})
            luck *= 0.7

        self.agents[name] = {
            "role": role,
            "stamina": stamina,
            "vitality": vitality,
            "strength": strength,
            "luck": luck,
            "skills": skills or [],
            "buffs": active_buffs or [],
            "debuffs": debuffs,
            "status": "Exhausted" if stamina < 20 else "Active",
            "last_update": time.time()
        }
        self.save_state()

    def add_buff(self, name, buff_name, icon, effect):
        """Ajana pozitif bir buff ekler."""
        if name in self.agents:
            if "buffs" not in self.agents[name]:
                self.agents[name]["buffs"] = []
            # Varsa eskini sil, yenisini ekle
            self.agents[name]["buffs"] = [b for b in self.agents[name]["buffs"] if b["name"] != buff_name]
            self.agents[name]["buffs"].append({"name": buff_name, "icon": icon, "effect": effect})
            self.save_state()
            return True
        return False

    def compress_agent(self, name):
        """Ajanı /compress komutuyla dinlendirir (Stamina tazeler, debuffları siler)."""
        if name in self.agents:
            self.agents[name]["stamina"] = 100
            self.agents[name]["debuffs"] = [] # Yorgunluk geçer
            self.agents[name]["status"] = "Rested & Compressing..."
            self.save_state()
            return True
        return False

    def save_state(self):
        with open(self.state_file, 'w', encoding='utf-8') as f:
            json.dump(self.agents, f, indent=4, ensure_ascii=False)

    def _get_bar(self, value, color_icon="█"):
        bar_len = 15
        filled = int(value / (100 / bar_len))
        return color_icon * filled + "░" * (bar_len - filled)

    def render_all(self):
        """Dashboard tipi gelişmiş çoklu gösterim (Skills & Buffs dahil)."""
        output = ["\n" + "╔" + "═"*65 + "╗"]
        output.append("║" + " [ PARTY STATUS - ADVANCED RPG DASHBOARD ] ".center(65) + "║")
        output.append("╠" + "═"*65 + "╣")
        
        for name, data in self.agents.items():
            # Buff ve Debuffları birleştir
            status_icons = "".join([b["icon"] for b in data.get("buffs", [])])
            status_icons += "".join([d["icon"] for d in data.get("debuffs", [])])
            
            output.append(f"║ 👤 {name:<12} {status_icons:<10} | Role: {data['role']:<10} | Status: {data['status']:<11} ║")
            output.append(f"║ ⚡ STAMINA  [{self._get_bar(data['stamina'])}] {data['stamina']:>5.1f}% | ⚡ Context Limit   ║")
            output.append(f"║ ❤️ VITALITY [{self._get_bar(data['vitality'])}] {data['vitality']:>5.1f}% | ❤️ Error Rate      ║")
            output.append(f"║ 💪 STRENGTH [{self._get_bar(data['strength'])}] {data['strength']:>5.1f}% | 💪 Reasoning Power ║")
            output.append(f"║ 🍀 LUCK     [{self._get_bar(data['luck'])}] {data['luck']:>5.1f}% | 🍀 Accuracy Rate  ║")
            
            # Skills Row
            skills_icons = " ".join([s["icon"] for s in data.get("skills", [])])
            output.append(f"║ 🛠️  SKILLS: {skills_icons:<52} ║")
            
            # Buff/Debuff Details (Brief)
            effects = [f"{b['name']}({b['icon']})" for b in data.get("buffs", [])]
            effects += [f"{d['name']}({d['icon']})" for d in data.get("debuffs", [])]
            if effects:
                effects_str = " | ".join(effects)
                output.append(f"║ ✨ STATUS: {effects_str[:53]:<53} ║")
                
            output.append("╟" + "─"*65 + "╢")
        
        output.append("╚" + "═"*65 + "╝")
        return "\n".join(output)

if __name__ == "__main__":
    manager = MultiAgentRPGManager()
    
    # Skills Tanımları
    s_analist = [{"name": "Search", "icon": "🔍"}, {"name": "Memory", "icon": "🧠"}]
    s_fetch = [{"name": "Web", "icon": "🌐"}, {"name": "Auth", "icon": "🔑"}]
    s_design = [{"name": "Code", "icon": "💻"}, {"name": "Visual", "icon": "🎨"}]

    # Test verileri
    manager.update_agent("AnalistAgent", "Research", 12000, skills=s_analist)
    manager.add_buff("AnalistAgent", "FOCUSED", "🔥", "+10% Luck")
    
    manager.update_agent("FetchAgent", "WebData", 48000, errors=1, skills=s_fetch)
    
    # Yorgun Ajan Testi (Fatigue Debuff otomatik tetiklenecek)
    manager.update_agent("DesignAgent", "UI/UX", 105000, errors=2, reasoning_effort=95, skills=s_design)
    
    print(manager.render_all())
