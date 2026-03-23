"""
Usage:
  python -m src.main --draft "Your story idea here" --style "Cinematic Realism"
  python -m src.main --draft "Your story idea here" --style "Anime / Ghibli" --create-images
"""
import asyncio
import argparse
import json
from dotenv import load_dotenv

from src.graph import graph
from src.prompts import GRAPHIC_STYLES

load_dotenv()


async def run(draft: str, graphic_style: str, is_create_image: bool):
    print(f"\nRunning screenplay agent pipeline...")
    print(f"   Style: {graphic_style}")
    print(f"   Generate images: {is_create_image}\n")

    result = await graph.ainvoke({
        "draft": draft,
        "graphic_style": graphic_style,
        "is_create_image": is_create_image,
        "completed_script": "",
        "styled_script": "",
        "scenes": [],
        "scenes_with_prompts": [],
        "final_scenes": [],
    })

    final_scenes = result.get("final_scenes") or result.get("scenes_with_prompts", [])

    print("\n=== STYLED SCRIPT ===")
    print(result["styled_script"])

    print("\n=== SCENES ===")
    for scene in final_scenes:
        data = scene.model_dump() if hasattr(scene, "model_dump") else scene
        print(json.dumps(data, ensure_ascii=False, indent=2))

    return result


def main():
    parser = argparse.ArgumentParser(description="Screenplay Agent Flow")
    parser.add_argument("--draft", required=True, help="Raw screenplay draft text")
    parser.add_argument(
        "--style",
        default="Cinematic Realism",
        choices=list(GRAPHIC_STYLES.keys()),
        help="Graphic style for image prompts",
    )
    parser.add_argument("--create-images", action="store_true", help="Generate images via Pollinations.ai")
    args = parser.parse_args()

    asyncio.run(run(args.draft, args.style, args.create_images))


if __name__ == "__main__":
    main()
