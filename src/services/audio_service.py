from pathlib import Path
from typing import Optional
from ..config import settings

AUDIO_ROOT = Path(settings.AUDIO_STORAGE_PATH)

def resolve_audio_path(dua_audio_map: dict, reciter: str) -> Optional[Path]:
    if not dua_audio_map:
        return None

    candidate = dua_audio_map.get(reciter)
    if not candidate:
        return None

    if candidate.startswith("http://") or candidate.startswith("https://"):
        return None

    p = Path(candidate)
    if not p.is_absolute():
        p = AUDIO_ROOT / p
    if p.exists():
        return p
    return None

def audio_url_is_remote(dua_audio_map: dict, reciter: str) -> Optional[str]:
    if not dua_audio_map:
        return None
    candidate = dua_audio_map.get(reciter)
    if not candidate:
        return None
    if candidate.startswith("http://") or candidate.startswith("https://"):
        return candidate
    return None
