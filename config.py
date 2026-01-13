from pathlib import Path
from sqlalchemy import create_engine

# --- 設定 ---
DB_PATH = "resonancetables.sqlite"
DATA_ROOT = Path("/Volumes/LaCie/resonancetables")


engine = create_engine(f"sqlite:///{DB_PATH}")

