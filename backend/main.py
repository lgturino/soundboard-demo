from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse

app = FastAPI()

BASE_DIR = Path(__file__).resolve().parent.parent
AUDIO_DIR = BASE_DIR / "backend" / "audio"
FRONTEND_FILE = BASE_DIR / "frontend" / "index.html"
SCRIPT_FILE = BASE_DIR / "frontend" / "main.js"


@app.get("/api/audio")
async def list_audio() -> list[str]:
    if not AUDIO_DIR.exists():
        return []
    return sorted(path.name for path in AUDIO_DIR.iterdir() if path.is_file() and path.suffix.lower() == ".mp3")


@app.get("/api/audio/{name}")
async def get_audio(name: str):
    if Path(name).name != name or Path(name).suffix.lower() != ".mp3":
        raise HTTPException(status_code=404)
    path = AUDIO_DIR / name
    if not path.is_file():
        raise HTTPException(status_code=404)
    return FileResponse(path, media_type="audio/mpeg")


@app.delete("/api/audio/{name}", status_code=204)
async def delete_audio(name: str):
    if Path(name).name != name or Path(name).suffix.lower() != ".mp3":
        raise HTTPException(status_code=404)
    path = AUDIO_DIR / name
    try:
        path.unlink()
    except FileNotFoundError:
        raise HTTPException(status_code=404)


@app.get("/")
async def root():
    return FileResponse(FRONTEND_FILE)


@app.get("/main.js")
async def main_script():
    return FileResponse(SCRIPT_FILE, media_type="text/javascript")
