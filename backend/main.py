from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse

import random

app = FastAPI()

BASE_DIR = Path(__file__).resolve().parent.parent
AUDIO_DIR = BASE_DIR / "backend" / "audio"
FRONTEND_FILE = BASE_DIR / "frontend" / "index.html"
SCRIPT_FILE = BASE_DIR / "frontend" / "main.js"

class AudioStore:
    def __init__(self, directory: Path):
        self.directory: Path = directory
        self.files = []
        self.selected_files: list[str] = []
        self.selected_files_id: list[int] = []
        self.selected_rep: str = ""

    def refresh_files(self) -> list[str]:
        if not self.directory.exists():
            self.files = []
        else:
            self.files = sorted(path.name for path in AUDIO_DIR.iterdir() if path.is_file() and path.suffix.lower() == ".mp3")
        return self.files

    def delete_file(self, name: str):
        if Path(name).name != name or Path(name).suffix.lower() != ".mp3":
            raise HTTPException(status_code=404)
        path = self.directory / name
        try:
            path.unlink()
            self.refresh_files()
        except FileNotFoundError:
            raise HTTPException(status_code=404)

    def get_random_selection(self, k: int):
        l = len(self.files)
        # choose k files to play
        self.selected_files_id = random.sample(range(0, l), k=k)
        self.selected_rep = ", ".join(str(num) for num in self.selected_files)
        self.selected_files = [self.files[fid] for fid in self.selected_files_id]


    def set_selection(self, s: str):
        self.selected_rep = s
        self.selected_files_id = [int(num.strip()) for num in s.split(",")]
        self.selected_files = [self.files[fid] for fid in self.selected_files_id]

sounds = AudioStore(AUDIO_DIR)
sounds.refresh_files() # initial setup

@app.get("/api/audio")
async def list_audio() -> list[str]:
    return sounds.files

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
    sounds.delete_file(name)

@app.get("/")
async def root():
    return FileResponse(FRONTEND_FILE)


@app.get("/main.js")
async def main_script():
    return FileResponse(SCRIPT_FILE, media_type="text/javascript")
