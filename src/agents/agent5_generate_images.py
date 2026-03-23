import asyncio
from pathlib import Path

import httpx

from src.state import GraphState
from src.agents.tools.image_tools import build_image_url, fetch_image


async def agent5_generate_images(state: GraphState) -> dict:
    output_dir = Path("output/scenes")
    output_dir.mkdir(parents=True, exist_ok=True)

    async with httpx.AsyncClient() as client:
        tasks = [
            fetch_image(client, scene, output_dir)
            for scene in state["scenes_with_prompts"]
        ]
        final_scenes = await asyncio.gather(*tasks)

    return {"final_scenes": list(final_scenes)}
