"""Apply all database migrations: python tools/migrate.py"""
from pathlib import Path
import subprocess,sys
root=Path(__file__).resolve().parents[1]
raise SystemExit(subprocess.call([sys.executable,'-m','alembic','-c',str(root/'alembic.ini'),'upgrade','head'],cwd=root))
