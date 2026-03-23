"""
FastAPI server for the Screenplay Agent Flow UI.

Run:
    python server.py
Then open http://localhost:8000
"""
import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

load_dotenv()

from src.graph import graph
from src.prompts import GRAPHIC_STYLES

app = FastAPI()

# Serve static files (the single-page UI)
static_dir = Path(__file__).parent / "static"
static_dir.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory=static_dir), name="static")


class RunRequest(BaseModel):
    draft: str
    graphic_style: str = "Cinematic Realism"
    is_create_image: bool = False


@app.get("/")
async def index():
    return FileResponse(static_dir / "index.html")


@app.get("/styles")
async def get_styles():
    return list(GRAPHIC_STYLES.keys())


@app.post("/run")
async def run_pipeline(req: RunRequest):
    if req.graphic_style not in GRAPHIC_STYLES:
        return JSONResponse(status_code=400, content={"error": f"Unknown style: {req.graphic_style}"})

    result = await graph.ainvoke({
        "draft": req.draft,
        "graphic_style": req.graphic_style,
        "is_create_image": req.is_create_image,
        "completed_script": "",
        "styled_script": "",
        "scenes": [],
        "scenes_with_prompts": [],
        "final_scenes": [],
    })

    final_scenes = result.get("final_scenes") or result.get("scenes_with_prompts", [])

    return {
        "styled_script": result.get("styled_script", ""),
        "scenes": [s.model_dump() for s in final_scenes],
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
