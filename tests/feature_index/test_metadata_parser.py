import sys
import os
from pathlib import Path

import importlib.util
from pathlib import Path

# Proje kök dizinini ekle
core_path = Path(__file__).parent.parent.parent / "core"
sys.path.append(str(core_path))

# build_skill_index.py dosyasını asen import et
spec = importlib.util.spec_from_file_location("build_skill_index", str(core_path / "build_skill_index.py"))
build_skill_index = importlib.util.module_from_spec(spec)
spec.loader.exec_module(build_skill_index)

def test_frontmatter_parsing():
    content = """---
id: rule--nexus--test
type: rule
context: global
extends: rule--nexus--master
tags: test, validation
---
# Test Content
This is a test rule."""
    
    metadata = build_skill_index.parse_frontmatter(content)
    print(f"Parsed Metadata: {metadata}")
    
    assert metadata.get("id") == "rule--nexus--test"
    assert metadata.get("type") == "rule"
    assert metadata.get("extends") == "rule--nexus--master"
    print("✅ Metadata parsing test passed!")

if __name__ == "__main__":
    try:
        test_frontmatter_parsing()
    except Exception as e:
        print(f"❌ Test failed: {e}")
        sys.exit(1)
