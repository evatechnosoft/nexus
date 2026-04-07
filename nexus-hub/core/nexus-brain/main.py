from fastapi import APIRouter, HTTPException
import os
import json

router = APIRouter(prefix="/ops", tags=["Operations"])

BRAIN_PATH = "/DATA/projects/agentops-nexus/brain"
SKILLS_PATH = "/DATA/projects/agentops-nexus/skills"
MAP_PATH = "/DATA/projects/agentops-nexus/brain/nexus-skill-map.json"

@router.get("/brain/index")
async def get_brain_index():
    """Hafif zekâ dizinini (Index) döner."""
    index_file = os.path.join(SKILLS_PATH, "INDEX.md")
    if not os.path.exists(index_file):
        raise HTTPException(status_code=404, detail="Brain index not found")
    
    with open(index_file, "r", encoding="utf-8") as f:
        content = f.read()
    
    return {"index": content}

@router.post("/brain/resolve")
async def resolve_brain_context(request: dict):
    """
    İstek üzerine spesifik zekâ parçasını (Skill/Rule/Guide) döner.
    Payload: {"type": "skill", "name": "flutter-guidelines"}
    """
    req_type = request.get("type")
    req_name = request.get("name")
    
    # Harita dosyasını oku (Basit eşleme şimdilik)
    # Gerçek uygulamada nexus-skill-map.json parse edilecek.
    
    mapping = {
        "skill": os.path.join(BRAIN_PATH, "ai-memory"),
        "rule": os.path.join(BRAIN_PATH, "claude-rules"),
        "guide": "/DATA/projects/agentops-nexus/guides" # Henüz yoksa oluşacak
    }
    
    target_dir = mapping.get(req_type)
    if not target_dir:
        raise HTTPException(status_code=400, detail="Invalid resource type")
    
    # Dosyayı bul (Basit bir arama mantığı)
    target_file = None
    for root, dirs, files in os.walk(target_dir):
        for file in files:
            if req_name in file:
                target_file = os.path.join(root, file)
                break
    
    if not target_file or not os.path.exists(target_file):
        raise HTTPException(status_code=404, detail=f"Resource {req_name} not found")
        
    with open(target_file, "r", encoding="utf-8") as f:
        content = f.read()
        
    return {
        "name": req_name,
        "type": req_type,
        "content": content
    }
