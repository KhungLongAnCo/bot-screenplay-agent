from pathlib import Path
from urllib.parse import quote

import httpx

from src.state import Scene


def build_image_url(scene: Scene) -> str:
    encoded = quote(scene.image_prompt, safe="")
    seed = scene.scene_number * 42
    return (
        f"https://image.pollinations.ai/prompt/{encoded}"
        f"?width=768&height=432&nologo=true&seed={seed}"
    )


async def fetch_image(client: httpx.AsyncClient, scene: Scene, output_dir: Path) -> Scene:
    url = build_image_url(scene)
    response = await client.get(url, follow_redirects=True, timeout=60.0)
    response.raise_for_status()
    save_path = output_dir / f"scene_{scene.scene_number:02d}.jpg"
    save_path.write_bytes(response.content)
    return scene.model_copy(update={"image_url": str(save_path)})
