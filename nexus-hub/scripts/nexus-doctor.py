import os
import sys
import subprocess
import json
import platform
from pathlib import Path

# Add core to path for imports
core_path = Path(__file__).parent.parent / "core"
sys.path.append(str(core_path))

try:
    from nexus_logger import get_nexus_logger
    logger = get_nexus_logger("nexus-doctor")
except ImportError:
    # Fallback if nexus_logger is not found
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("nexus-doctor")

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

class NexusDoctor:
    def __init__(self):
        self.issues = []
        # Current file is in /scripts, so parent is project root
        self.root_dir = Path(__file__).parent.parent
        self.nexus_hub_dir = self.root_dir

    def check_python(self):
        logger.info("Checking Python environment...")
        logger.info(f"Python Version: {sys.version}")
        logger.info(f"Platform: {platform.system()} {platform.release()}")
        
        # Check if running in Docker
        is_docker = os.path.exists('/.dockerenv') or (os.path.exists('/proc/1/cgroup') and 'docker' in open('/proc/1/cgroup').read())
        if is_docker:
            logger.info("Running inside a Docker container. Venv check skipped.")
            return

        # Check if running in a venv
        is_venv = sys.prefix != sys.base_prefix
        if not is_venv:
            logger.warning("Not running in a virtual environment. It is recommended to use a venv.")
            self.issues.append("Sanal ortam (venv) kullanılmıyor. Bağımlılık çakışmaları yaşanabilir.")
        else:
            logger.info("Running in a virtual environment.")

    def check_directories(self):
        logger.info("Checking directory structure...")
        # If in docker, workdir is /app
        is_docker = os.path.exists('/.dockerenv')
        base = Path("/app") if is_docker else self.root_dir

        required_dirs = [
            "core",
            "scripts",
            "data/memory",
            "data/skills",
            "data/vault"
        ]
        
        for d in required_dirs:
            p = base / d
            if p.exists():
                logger.debug(f"Found directory: {d}")
            else:
                # Inside docker, some dirs might be mapped or created at runtime
                if is_docker and d.startswith("data"):
                     logger.info(f"Directory {d} will be created at runtime in container.")
                     continue
                logger.error(f"Missing directory: {d}")
                self.issues.append(f"Eksik dizin: {d}")

    def check_files(self):
        logger.info("Checking critical files...")
        required_files = [
            "core/nexus_mcp_server.py",
            "core/nexus_store.py",
            "core/nexus_logger.py",
            "core/nexus_schema.json",
            "core/.env.example"
        ]
        
        for f in required_files:
            p = self.root_dir / f
            if p.exists():
                logger.debug(f"Found file: {f}")
            else:
                logger.error(f"Missing file: {f}")
                self.issues.append(f"Eksik kritik dosya: {f}")

    def check_env_vars(self):
        logger.info("Checking environment variables...")
        # Try to load .env if it exists
        env_path = self.root_dir / ".env"
        if not env_path.exists():
            logger.warning(".env file not found in root. Checking system env vars.")
            self.issues.append(".env dosyası ana dizinde bulunamadı. Lütfen .env.example dosyasını kopyalayıp düzenleyin.")
        
        # Keys that are good to have
        keys = ["OPENAI_API_KEY", "GROQ_API_KEY", "NEXUS_VAULT_TOKEN"]
        for k in keys:
            if os.getenv(k):
                logger.info(f"Found env var: {k}")
            else:
                logger.warning(f"Env var not set: {k}")

    def check_mcp_connection(self):
        logger.info("Checking Nexus MCP Server status...")
        # Since we are likely on the same machine, we can check if it's reachable or if the process is running
        # This is a bit complex for a script, but we can try a simple ping if a URL is provided
        url = os.getenv("NEXUS_HUB_URL", "http://192.168.1.186:8900")
        try:
            # We use subprocess to avoid adding another dependency like 'requests' if it's not there
            # But wait, we should assume basic python tools. Let's use urllib.
            from urllib import request
            with request.urlopen(url + "/health", timeout=2) as response:
                if response.getcode() == 200:
                    logger.info(f"Nexus MCP Server ({url}) is UP and Healthy.")
                else:
                    logger.warning(f"Nexus MCP Server returned status {response.getcode()}")
        except Exception as e:
            logger.error(f"Could not connect to Nexus MCP Server at {url}: {e}")
            self.issues.append(f"Nexus MCP sunucusuna ({url}) erişilemiyor. Servisin çalıştığından emin olun.")

    def report_to_server(self):
        """Report issue count to Nexus metrics endpoint."""
        url = os.getenv("NEXUS_HUB_URL", "http://localhost:8900")
        try:
            from urllib import request
            import json
            data = json.dumps({"issues_count": len(self.issues)}).encode("utf-8")
            req = request.Request(
                f"{url}/api/doctor/report",
                data=data,
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            with request.urlopen(req, timeout=2) as response:
                if response.getcode() == 200:
                    logger.info("Reported health status to Nexus server.")
        except Exception as e:
            logger.debug(f"Failed to report to server: {e}")

    def run_all(self, report=True):
        logger.info("--- NEXUS DOCTOR STARTING ---")
        self.check_python()
        self.check_directories()
        self.check_files()
        self.check_env_vars()
        self.check_mcp_connection()
        
        if report:
            self.report_to_server()
        
        print("\n" + "="*50)
        if not self.issues:
            logger.info("NEXUS SYSTEM IS HEALTHY! No issues found.")
            print("SAĞLIK RAPORU: SİSTEM SAĞLIKLI")
        else:
            logger.warning(f"Found {len(self.issues)} issues. See details below:")
            print("SAĞLIK RAPORU: EKSİKLER BULUNDU")
            for i, issue in enumerate(self.issues, 1):
                print(f"{i}. {issue}")
        print("="*50 + "\n")

if __name__ == "__main__":
    doctor = NexusDoctor()
    doctor.run_all()
