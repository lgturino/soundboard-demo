from pathlib import Path

from fastapi import FastAPI, HTTPException, Form, File, UploadFile
from fastapi.responses import FileResponse

import random
import shutil

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
        if k > l:
            k = l
        # choose k files to play
        self.selected_files_id = random.sample(range(1, l+1), k=k)
        self.selected_rep = ", ".join(str(num) for num in self.selected_files_id)
        self.selected_files = [self.files[fid-1] for fid in self.selected_files_id]

        return self.selected_files

    def set_selection(self, s: str):

        parts = [part.strip() for part in s.split(",")]
        if not parts or any(not part.isdecimal() for part in parts):
            raise HTTPException(
                status_code=400,
                detail="invalid format: enter file numbers separated by commas"
            )

        self.selected_rep = s
        self.selected_files_id = [int(num.strip()) for num in s.split(",")]
        self.selected_files = [self.files[(fid - 1) % len(self.files)] for fid in self.selected_files_id]

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

@app.post("/api/rand")
async def get_rand(val: int = Form(...)):
    return sounds.get_random_selection(val)

@app.get("/api/selected")
async def get_selected() -> list[str]:
    return [ sounds.selected_rep ] + sounds.selected_files


@app.get("/api/selected-rep")
async def get_selected() -> str:
    return sounds.selected_rep

@app.post("/api/selected-rep")
async def set_selected(rep: str = Form(...)):
    sounds.set_selection(rep)
    return sounds.selected_files

@app.delete("/api/audio/{name}", status_code=204)
async def delete_audio(name: str):
    sounds.delete_file(name)

@app.post("/api/audio", status_code=201)
async def upload_audio(file: UploadFile = File(...)):
    name = Path(file.filename or "").name
    if not name or Path(name).suffix.lower() != ".mp3":
        raise HTTPException(status_code=400, detail="Choose an MP3 file")

    AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    destination = AUDIO_DIR / name
    if destination.exists():
        raise HTTPException(status_code=409, detail="A file with that name already exists, delete it first")

    with destination.open("xb") as output:
        shutil.copyfileobj(file.file, output)

    sounds.refresh_files()
    return {"name": name}

@app.get("/")
async def root():
    return FileResponse(FRONTEND_FILE)


@app.get("/main.js")
async def main_script():
    return FileResponse(SCRIPT_FILE, media_type="text/javascript")
