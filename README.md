# bot-screenplay-agent

A 5-agent LangGraph pipeline that transforms a raw screenplay draft into structured scenes with optional AI-generated images.

## Agent Flow

```
User Draft
    │
    ▼
┌─────────────────────────────────────────────────────────┐
│  Agent 1 · Analyze                                      │
│  Develops raw draft into a full 3-act screenplay        │
│  outline (3–5 key scenes, narrative prose)              │
└────────────────────────┬────────────────────────────────┘
                         │  completed_script
                         ▼
┌─────────────────────────────────────────────────────────┐
│  Agent 2 · Style                                        │
│  Rewrites outline into standard cinematic format        │
│  (INT/EXT headings, action lines, dialogue)             │
└────────────────────────┬────────────────────────────────┘
                         │  styled_script
                         ▼
┌─────────────────────────────────────────────────────────┐
│  Agent 3 · Split Scenes                                 │
│  Parses styled script into structured Scene objects     │
│  (scene_number, title, location, scene_script)          │
└────────────────────────┬────────────────────────────────┘
                         │  scenes[]
                         ▼
┌─────────────────────────────────────────────────────────┐
│  Agent 4 · Image Prompts                                │
│  Generates a visual image prompt for each scene         │
│  based on the selected graphic style                    │
└────────────────────────┬────────────────────────────────┘
                         │  scenes_with_prompts[]
                         │
              is_create_image?
                 /          \
               YES            NO
                │              │
                ▼              ▼
┌──────────────────────┐     END
│  Agent 5 · Images    │
│  Fetches AI-generated│
│  image from          │
│  Pollinations.ai     │
│  for each scene      │
└──────────┬───────────┘
           │  final_scenes[]
           ▼
          END
```

## State Schema

| Field                 | Type          | Description                         |
| --------------------- | ------------- | ----------------------------------- |
| `draft`               | `str`         | Raw input from the user             |
| `graphic_style`       | `str`         | Visual style for image generation   |
| `is_create_image`     | `bool`        | Whether to run Agent 5              |
| `completed_script`    | `str`         | Output of Agent 1                   |
| `styled_script`       | `str`         | Output of Agent 2                   |
| `scenes`              | `List[Scene]` | Output of Agent 3                   |
| `scenes_with_prompts` | `List[Scene]` | Output of Agent 4                   |
| `final_scenes`        | `List[Scene]` | Output of Agent 5 (with image URLs) |

## Graphic Styles

- Cinematic Realism
- Anime / Ghibli
- Watercolor Illustration
- Graphic Novel
- Dark Fantasy
- Vintage Film

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Add your OPENAI_API_KEY to .env
```

## Run

**Web UI:**

```bash
python server.py
# Open http://localhost:8000
```

**CLI:**

```bash
python -m src.main --draft "Your story idea" --style "Cinematic Realism"
python -m src.main --draft "Your story idea" --style "Anime / Ghibli" --create-images
```

## Tech Stack

- [LangGraph](https://github.com/langchain-ai/langgraph) — agent orchestration
- [LangChain OpenAI](https://github.com/langchain-ai/langchain) — LLM calls via `gpt-5-nano`
- [Pollinations.ai](https://pollinations.ai) — free AI image generation
- [FastAPI](https://fastapi.tiangolo.com) + [uvicorn](https://www.uvicorn.org) — web server
- [Pydantic v2](https://docs.pydantic.dev) — structured data models
