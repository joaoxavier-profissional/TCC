"""Caminhos compartilhados; BASE aponta para a raiz do projeto."""
from pathlib import Path
BASE = Path(__file__).resolve().parent.parent
BANCO = BASE / "cftv.db"
VIDEOS = BASE / "videos"
