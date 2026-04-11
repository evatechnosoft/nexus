import os
import hvac
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

# Vault'tan Secret Çekme (Gerçek Parametreler)
def get_db_url_from_vault():
    vault_url = os.getenv("VAULT_URL", "http://192.168.1.186:8200")
    vault_token = os.getenv("VAULT_TOKEN", "nexus-root-token")
    secret_path = os.getenv("VAULT_SECRET_PATH", "inventory/db")
    
    try:
        client = hvac.Client(url=vault_url, token=vault_token)
        # KV-V2 okuma mantığı
        read_response = client.secrets.kv.v2.read_secret_version(mount_point="nexus", path=secret_path)
        return read_response['data']['data']['DATABASE_URL']
    except Exception as e:
        print(f"Vault error: {e}")
        return os.getenv("DATABASE_URL", "postgresql://user:password@localhost/nexus_inventory")

SQLALCHEMY_DATABASE_URL = get_db_url_from_vault()
print(f"Connecting to DB via Vault: {SQLALCHEMY_DATABASE_URL[:25]}...")
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
