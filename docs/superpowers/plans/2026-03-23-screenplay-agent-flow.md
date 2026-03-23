# Screenplay Agent Flow Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a LangGraph multi-agent pipeline that transforms a raw screenplay draft into structured scenes with image prompts and optional AI-generated illustrations.

**Architecture:** Five sequential agents share a `GraphState` TypedDict — each agent reads from the state, calls Claude, and writes its output back. A conditional edge after Agent 4 routes to Agent 5 (image generation) or END based on `is_create_image`.

**Tech Stack:** Python 3.11+, LangGraph, langchain-anthropic (claude-sonnet-4-20250514), Pydantic v2, httpx (async), pytest + pytest-asyncio

---

## File Map

| File | Responsibility |
|---|---|
| `src/state.py` | `Scene` Pydantic model + `GraphState` TypedDict |
| `src/prompts.py` | All system prompts + reference script constant |
| `src/agents/agent1_analyze.py` | Analyze & complete raw draft |
| `src/agents/agent2_style.py` | Rewrite in cinematic format |
| `src/agents/agent3_split_scenes.py` | Split script → `List[Scene]` JSON |
| `src/agents/agent4_image_prompts.py` | Add `image_prompt` to each scene |
| `src/agents/agent5_generate_images.py` | Fetch image URLs from Pollinations.ai |
| `src/graph.py` | Assemble and compile LangGraph graph |
| `src/main.py` | CLI entry point (`python -m src.main`) |
| `tests/test_state.py` | State schema validation |
| `tests/test_prompts.py` | Prompt template formatting validation |
| `tests/test_agents.py` | Agent functions with mocked LLM |
| `tests/test_graph.py` | Graph routing logic |
| `tests/test_main.py` | CLI argument parsing |
| `requirements.txt` | Dependencies |
| `.env.example` | Required env vars |

---

## Task 1: Project Scaffold

**Files:**
- Create: `requirements.txt`
- Create: `.env.example`
- Create: `src/__init__.py`
- Create: `src/agents/__init__.py`
- Create: `tests/__init__.py`
- Create: `pyproject.toml`

- [ ] **Step 1: Create `requirements.txt`**

```
langgraph>=0.2.74
langchain-anthropic>=0.3.0
langchain-core>=0.3.0
pydantic>=2.0.0
httpx>=0.27.0
python-dotenv>=1.0.0
pytest>=8.0.0
pytest-asyncio>=0.23.0
```

- [ ] **Step 2: Create `pyproject.toml`**

```toml
[build-system]
requires = ["setuptools>=68"]
build-backend = "setuptools.build_meta"

[project]
name = "screenplay-agent-flow"
version = "0.1.0"
requires-python = ">=3.11"

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
```

- [ ] **Step 3: Create `.env.example`**

```
ANTHROPIC_API_KEY=sk-ant-...
# Optional LangSmith tracing
LANGCHAIN_TRACING_V2=false
LANGCHAIN_PROJECT=screenplay-agent-flow
LANGCHAIN_API_KEY=ls__...
```

- [ ] **Step 4: Create empty `__init__.py` files**

```bash
touch src/__init__.py src/agents/__init__.py tests/__init__.py
```

- [ ] **Step 5: Install dependencies**

```bash
pip install -r requirements.txt
```

- [ ] **Step 6: Commit**

```bash
git init
git add .
git commit -m "chore: project scaffold"
```

---

## Task 2: State Models

**Files:**
- Create: `src/state.py`
- Create: `tests/test_state.py`

- [ ] **Step 1: Write failing test**

```python
# tests/test_state.py
from src.state import Scene, GraphState
from typing import get_type_hints

def test_scene_defaults():
    scene = Scene(scene_number=1, title="Opening", location="INT. CAFE - DAY", scene_script="...")
    assert scene.image_prompt is None
    assert scene.image_url is None

def test_scene_full():
    scene = Scene(
        scene_number=2,
        title="Climax",
        location="EXT. ROOFTOP - NIGHT",
        scene_script="Hero stands at the edge.",
        image_prompt="cinematic realism, dramatic lighting",
        image_url="https://image.pollinations.ai/prompt/..."
    )
    assert scene.scene_number == 2
    assert scene.image_url is not None

def test_graph_state_keys():
    hints = get_type_hints(GraphState)
    required = {"draft", "graphic_style", "is_create_image", "completed_script",
                "styled_script", "scenes", "scenes_with_prompts", "final_scenes"}
    assert required.issubset(hints.keys())
```

- [ ] **Step 2: Run test — expect FAIL**

```bash
pytest tests/test_state.py -v
```
Expected: `ModuleNotFoundError: No module named 'src.state'`

- [ ] **Step 3: Implement `src/state.py`**

```python
from typing import TypedDict, List, Optional
from pydantic import BaseModel


class Scene(BaseModel):
    scene_number: int
    title: str
    location: str
    scene_script: str
    image_prompt: Optional[str] = None
    image_url: Optional[str] = None


class GraphState(TypedDict):
    # User inputs
    draft: str
    graphic_style: str
    is_create_image: bool

    # Accumulated outputs
    completed_script: str       # Agent 1
    styled_script: str          # Agent 2
    scenes: List[Scene]         # Agent 3
    scenes_with_prompts: List[Scene]  # Agent 4
    final_scenes: List[Scene]   # Agent 5 or copy from Agent 4
```

- [ ] **Step 4: Run test — expect PASS**

```bash
pytest tests/test_state.py -v
```
Expected: `3 passed`

- [ ] **Step 5: Commit**

```bash
git add src/state.py tests/test_state.py
git commit -m "feat: add Scene and GraphState models"
```

---

## Task 3: Prompts

**Files:**
- Create: `src/prompts.py`
- Create: `tests/test_prompts.py`

- [ ] **Step 1: Write failing test**

```python
# tests/test_prompts.py
from src.prompts import GRAPHIC_STYLES, AGENT1_SYSTEM_PROMPT, AGENT2_SYSTEM_PROMPT, AGENT3_SYSTEM_PROMPT, AGENT4_SYSTEM_PROMPT, REFERENCE_SCRIPT

EXPECTED_STYLES = {
    "Cinematic Realism", "Anime / Ghibli", "Watercolor",
    "Graphic Novel", "Dark Fantasy", "Vintage Film",
}

def test_all_graphic_style_keys_exist():
    assert EXPECTED_STYLES == set(GRAPHIC_STYLES.keys())

def test_graphic_style_values_are_non_empty():
    for key, value in GRAPHIC_STYLES.items():
        assert value, f"Style '{key}' has empty value"

def test_agent2_prompt_has_reference_placeholder():
    # Must contain {reference} so .format(reference=...) works
    assert "{reference}" in AGENT2_SYSTEM_PROMPT

def test_agent4_prompt_has_graphic_style_placeholder():
    assert "{graphic_style}" in AGENT4_SYSTEM_PROMPT

def test_prompts_format_without_error():
    # Ensures no stray curly braces cause KeyError at runtime
    AGENT2_SYSTEM_PROMPT.format(reference=REFERENCE_SCRIPT)
    AGENT4_SYSTEM_PROMPT.format(graphic_style="cinematic realism, test")
```

- [ ] **Step 2: Run test — expect FAIL**

```bash
pytest tests/test_prompts.py -v
```
Expected: `ModuleNotFoundError: No module named 'src.prompts'`

- [ ] **Step 3: Create `src/prompts.py`**

```python
REFERENCE_SCRIPT = """INT. HANOI APARTMENT - DAWN

Pale light seeps through bamboo blinds. MINH (28) sits on the floor,
back against the bed, phone face-down. Three missed calls. He doesn't move.

                    MINH
          (barely audible)
     I'm still here.

The city hums below — motorbikes, vendors, rain hitting tin roofs.
He finally picks up the phone. Stares at the screen. Sets it back down.
"""

AGENT1_SYSTEM_PROMPT = """You are a Vietnamese screenplay development consultant.
The user gives you a raw draft — it may be just a few lines of idea.
Your job: develop it into a structured screenplay outline.

Rules:
- Analyze the central theme, characters, and emotional arc
- Build a 3-act structure: setup → confrontation → resolution
- Develop 3–5 key scenes
- Preserve the spirit of the original draft
- Output: flowing prose screenplay (no formatting yet)
- Language: match the input language (Vietnamese or English)"""

AGENT2_SYSTEM_PROMPT = """You are a professional screenplay formatter.
Rewrite the provided screenplay in standard cinematic format.

Reference this script for style — note the terse action lines,
sensory detail, and emotion shown through behavior, not narration:

---
{reference}
---

Format every scene as:
INT/EXT. LOCATION - TIME
[Action lines — present tense, lean, visual]

CHARACTER NAME
(parenthetical if needed)
Dialogue...

Rules:
- Short, punchy action lines
- Emotion through detail, not statement
- Vietnamese diacritics preserved exactly
- 3–8 scenes maximum"""

AGENT3_SYSTEM_PROMPT = """You are a screenplay parsing engine.
Split the provided formatted screenplay into individual scene objects.

Rules:
- Each INT. or EXT. slug line = one new scene
- Preserve the FULL scene content in scene_script verbatim
- scene_number starts at 1
- title: 3–5 word summary of the scene
- Minimum 3 scenes, maximum 8 scenes
- Output ONLY a valid JSON array — no explanation, no markdown"""

AGENT4_SYSTEM_PROMPT = """You are a visual art director for AI image generation.
For each scene, write one image prompt in English (50–80 words).

Graphic style to apply: {graphic_style}

Prompt structure:
1. Graphic style prefix (inject exactly as given)
2. Camera angle and lighting (wide shot / close-up / golden hour / etc.)
3. Characters — appearance, costume, emotion
4. Environment — location, time, atmosphere

Output ONLY a valid JSON array with the same scene objects plus imagePrompt field.
No explanation, no markdown."""

GRAPHIC_STYLES = {
    "Cinematic Realism": "cinematic realism, dramatic lighting, photorealistic, 8k film still",
    "Anime / Ghibli": "anime style, cel shading, Studio Ghibli inspired, vibrant colors",
    "Watercolor": "watercolor illustration, soft edges, painterly, editorial illustration",
    "Graphic Novel": "graphic novel, bold ink lines, high contrast, comic book panels",
    "Dark Fantasy": "dark fantasy, digital painting, atmospheric, dramatic shadows, concept art",
    "Vintage Film": "vintage film photography, 35mm grain, muted tones, 1970s aesthetic",
}
```

- [ ] **Step 4: Run tests — expect PASS**

```bash
pytest tests/test_prompts.py -v
```
Expected: `5 passed`

- [ ] **Step 5: Commit**

```bash
git add src/prompts.py tests/test_prompts.py
git commit -m "feat: add system prompts and graphic style presets"
```

---

## Task 4: Agent 1 — Analyze & Complete

**Files:**
- Create: `src/agents/agent1_analyze.py`
- Create: `tests/test_agents.py` (first test)

- [ ] **Step 1: Write failing test**

```python
# tests/test_agents.py
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from src.agents.agent1_analyze import agent1_analyze
from src.state import GraphState, Scene

def make_state(**overrides) -> GraphState:
    base: GraphState = {
        "draft": "A young woman returns to her hometown after 10 years.",
        "graphic_style": "Cinematic Realism",
        "is_create_image": False,
        "completed_script": "",
        "styled_script": "",
        "scenes": [],
        "scenes_with_prompts": [],
        "final_scenes": [],
    }
    base.update(overrides)
    return base

def test_agent1_returns_completed_script():
    state = make_state()
    mock_chain = MagicMock()
    mock_chain.invoke.return_value = "Completed screenplay text here."

    with patch("src.agents.agent1_analyze.build_chain", return_value=mock_chain):
        result = agent1_analyze(state)

    assert "completed_script" in result
    assert result["completed_script"] == "Completed screenplay text here."
    mock_chain.invoke.assert_called_once_with({"draft": state["draft"]})
```

- [ ] **Step 2: Run test — expect FAIL**

```bash
pytest tests/test_agents.py::test_agent1_returns_completed_script -v
```
Expected: `ModuleNotFoundError`

- [ ] **Step 3: Implement `src/agents/agent1_analyze.py`**

```python
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_anthropic import ChatAnthropic

from src.state import GraphState
from src.prompts import AGENT1_SYSTEM_PROMPT


def build_chain():
    llm = ChatAnthropic(model="claude-sonnet-4-20250514", max_tokens=3000)
    prompt = ChatPromptTemplate.from_messages([
        ("system", AGENT1_SYSTEM_PROMPT),
        ("human", "KỊCH BẢN DRAFT:\n{draft}"),
    ])
    return prompt | llm | StrOutputParser()


def agent1_analyze(state: GraphState) -> dict:
    chain = build_chain()
    result = chain.invoke({"draft": state["draft"]})
    return {"completed_script": result}
```

- [ ] **Step 4: Run test — expect PASS**

```bash
pytest tests/test_agents.py::test_agent1_returns_completed_script -v
```
Expected: `1 passed`

- [ ] **Step 5: Commit**

```bash
git add src/agents/agent1_analyze.py tests/test_agents.py
git commit -m "feat: agent1 analyze and complete screenplay"
```

---

## Task 5: Agent 2 — Cinematic Style

**Files:**
- Create: `src/agents/agent2_style.py`
- Modify: `tests/test_agents.py` (add test)

- [ ] **Step 1: Add failing test to `tests/test_agents.py`**

```python
from src.agents.agent2_style import agent2_style

def test_agent2_returns_styled_script():
    state = make_state(completed_script="Draft screenplay text.")
    mock_chain = MagicMock()
    mock_chain.invoke.return_value = "INT. CAFE - DAY\nFormatted text."

    with patch("src.agents.agent2_style.build_chain", return_value=mock_chain):
        result = agent2_style(state)

    assert result["styled_script"] == "INT. CAFE - DAY\nFormatted text."
    mock_chain.invoke.assert_called_once_with({"completed_script": state["completed_script"]})
```

- [ ] **Step 2: Run test — expect FAIL**

```bash
pytest tests/test_agents.py::test_agent2_returns_styled_script -v
```

- [ ] **Step 3: Implement `src/agents/agent2_style.py`**

```python
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_anthropic import ChatAnthropic

from src.state import GraphState
from src.prompts import AGENT2_SYSTEM_PROMPT, REFERENCE_SCRIPT


def build_chain():
    llm = ChatAnthropic(model="claude-sonnet-4-20250514", max_tokens=3000)
    prompt = ChatPromptTemplate.from_messages([
        ("system", AGENT2_SYSTEM_PROMPT.format(reference=REFERENCE_SCRIPT)),
        ("human", "{completed_script}"),
    ])
    return prompt | llm | StrOutputParser()


def agent2_style(state: GraphState) -> dict:
    chain = build_chain()
    result = chain.invoke({"completed_script": state["completed_script"]})
    return {"styled_script": result}
```

- [ ] **Step 4: Run test — expect PASS**

```bash
pytest tests/test_agents.py::test_agent2_returns_styled_script -v
```

- [ ] **Step 5: Commit**

```bash
git add src/agents/agent2_style.py tests/test_agents.py
git commit -m "feat: agent2 cinematic style rewrite"
```

---

## Task 6: Agent 3 — Split Scenes (Structured Output)

**Files:**
- Create: `src/agents/agent3_split_scenes.py`
- Modify: `tests/test_agents.py`

- [ ] **Step 1: Add failing test**

```python
from src.agents.agent3_split_scenes import agent3_split_scenes
from src.state import Scene

def test_agent3_returns_scene_list():
    state = make_state(styled_script="INT. CAFE - DAY\nA woman enters.\nEXT. STREET - NIGHT\nShe walks away.")
    mock_scenes = [
        Scene(scene_number=1, title="Cafe Arrival", location="INT. CAFE - DAY", scene_script="A woman enters."),
        Scene(scene_number=2, title="Night Walk", location="EXT. STREET - NIGHT", scene_script="She walks away."),
    ]

    with patch("src.agents.agent3_split_scenes.build_structured_chain") as mock_build:
        mock_chain = MagicMock()
        mock_chain.invoke.return_value = mock_scenes
        mock_build.return_value = mock_chain
        result = agent3_split_scenes(state)

    assert len(result["scenes"]) == 2
    assert result["scenes"][0].title == "Cafe Arrival"
```

- [ ] **Step 2: Run test — expect FAIL**

```bash
pytest tests/test_agents.py::test_agent3_returns_scene_list -v
```

- [ ] **Step 3: Implement `src/agents/agent3_split_scenes.py`**

```python
from typing import List
from langchain_core.prompts import ChatPromptTemplate
from langchain_anthropic import ChatAnthropic

from src.state import GraphState, Scene
from src.prompts import AGENT3_SYSTEM_PROMPT


def build_structured_chain():
    llm = ChatAnthropic(model="claude-sonnet-4-20250514", max_tokens=2500)
    structured_llm = llm.with_structured_output(List[Scene])
    prompt = ChatPromptTemplate.from_messages([
        ("system", AGENT3_SYSTEM_PROMPT),
        ("human", "{styled_script}"),
    ])
    return prompt | structured_llm


def agent3_split_scenes(state: GraphState) -> dict:
    chain = build_structured_chain()
    scenes: List[Scene] = chain.invoke({"styled_script": state["styled_script"]})
    return {"scenes": scenes}
```

- [ ] **Step 4: Run test — expect PASS**

```bash
pytest tests/test_agents.py::test_agent3_returns_scene_list -v
```

- [ ] **Step 5: Commit**

```bash
git add src/agents/agent3_split_scenes.py tests/test_agents.py
git commit -m "feat: agent3 split screenplay into scenes with structured output"
```

---

## Task 7: Agent 4 — Image Prompts

**Files:**
- Create: `src/agents/agent4_image_prompts.py`
- Modify: `tests/test_agents.py`

- [ ] **Step 1: Add failing test**

```python
from src.agents.agent4_image_prompts import agent4_image_prompts

def test_agent4_adds_image_prompt():
    scenes = [
        Scene(scene_number=1, title="Opening", location="INT. CAFE - DAY", scene_script="She enters."),
    ]
    state = make_state(scenes=scenes, graphic_style="Cinematic Realism")

    with patch("src.agents.agent4_image_prompts.generate_image_prompt") as mock_gen:
        mock_gen.return_value = "cinematic realism, dramatic lighting, woman entering cafe"
        result = agent4_image_prompts(state)

    assert len(result["scenes_with_prompts"]) == 1
    assert result["scenes_with_prompts"][0].image_prompt == "cinematic realism, dramatic lighting, woman entering cafe"

def test_agent4_preserves_scene_data():
    scenes = [
        Scene(scene_number=1, title="Opening", location="INT. CAFE - DAY", scene_script="She enters."),
    ]
    state = make_state(scenes=scenes, graphic_style="Anime / Ghibli")

    with patch("src.agents.agent4_image_prompts.generate_image_prompt", return_value="anime style"):
        result = agent4_image_prompts(state)

    s = result["scenes_with_prompts"][0]
    assert s.scene_number == 1
    assert s.scene_script == "She enters."
```

- [ ] **Step 2: Run tests — expect FAIL**

```bash
pytest tests/test_agents.py::test_agent4_adds_image_prompt tests/test_agents.py::test_agent4_preserves_scene_data -v
```

- [ ] **Step 3: Implement `src/agents/agent4_image_prompts.py`**

```python
from typing import List
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_anthropic import ChatAnthropic

from src.state import GraphState, Scene
from src.prompts import AGENT4_SYSTEM_PROMPT, GRAPHIC_STYLES


def generate_image_prompt(scene: Scene, graphic_style: str, llm) -> str:
    style_value = GRAPHIC_STYLES.get(graphic_style, graphic_style)
    prompt = ChatPromptTemplate.from_messages([
        ("system", AGENT4_SYSTEM_PROMPT.format(graphic_style=style_value)),
        ("human", "Scene {number}: {title}\nLocation: {location}\n\n{script}"),
    ])
    chain = prompt | llm | StrOutputParser()
    return chain.invoke({
        "number": scene.scene_number,
        "title": scene.title,
        "location": scene.location,
        "script": scene.scene_script,
    })


def agent4_image_prompts(state: GraphState) -> dict:
    llm = ChatAnthropic(model="claude-sonnet-4-20250514", max_tokens=3000)
    scenes_with_prompts: List[Scene] = []
    for scene in state["scenes"]:
        prompt_text = generate_image_prompt(scene, state["graphic_style"], llm)
        scenes_with_prompts.append(scene.model_copy(update={"image_prompt": prompt_text}))
    return {"scenes_with_prompts": scenes_with_prompts}
```

- [ ] **Step 4: Run tests — expect PASS**

```bash
pytest tests/test_agents.py -k "agent4" -v
```

- [ ] **Step 5: Commit**

```bash
git add src/agents/agent4_image_prompts.py tests/test_agents.py
git commit -m "feat: agent4 generate image prompts per scene"
```

---

## Task 8: Agent 5 — Generate Images

**Files:**
- Create: `src/agents/agent5_generate_images.py`
- Modify: `tests/test_agents.py`

- [ ] **Step 1: Add failing test**

```python
from urllib.parse import quote
from src.agents.agent5_generate_images import agent5_generate_images, build_image_url

def test_build_image_url():
    scene = Scene(scene_number=1, title="T", location="L", scene_script="S",
                  image_prompt="cinematic realism, woman in cafe")
    url = build_image_url(scene)
    assert "image.pollinations.ai" in url
    assert "width=768" in url
    assert "height=432" in url
    assert "nologo=true" in url
    # Verify the encoded prompt appears in the URL path
    assert quote("cinematic realism, woman in cafe", safe="") in url

@pytest.mark.asyncio
async def test_agent5_sets_image_url():
    scenes = [
        Scene(scene_number=1, title="T", location="L", scene_script="S",
              image_prompt="cinematic realism, dramatic scene"),
    ]
    state = make_state(scenes_with_prompts=scenes)

    mock_response = AsyncMock()
    mock_response.content = b"fake-image-bytes"
    mock_response.raise_for_status = MagicMock()

    mock_client = AsyncMock()
    mock_client.get.return_value = mock_response
    mock_client.__aenter__.return_value = mock_client
    mock_client.__aexit__.return_value = None

    mock_file = MagicMock()
    mock_file.write_bytes = MagicMock()
    mock_file.__str__ = lambda s: "output/scenes/scene_01.jpg"

    mock_dir = MagicMock()
    mock_dir.mkdir = MagicMock()
    # Dunder methods must be set on the type, not the instance
    type(mock_dir).__truediv__ = MagicMock(return_value=mock_file)

    with patch("src.agents.agent5_generate_images.httpx.AsyncClient", return_value=mock_client):
        with patch("src.agents.agent5_generate_images.Path", return_value=mock_dir):
            result = await agent5_generate_images(state)

    assert len(result["final_scenes"]) == 1
    assert result["final_scenes"][0].image_url is not None
    assert isinstance(result["final_scenes"][0].image_url, str)
```

- [ ] **Step 2: Run test — expect FAIL**

```bash
pytest tests/test_agents.py::test_build_image_url tests/test_agents.py::test_agent5_sets_image_url -v
```

- [ ] **Step 3: Implement `src/agents/agent5_generate_images.py`**

```python
import asyncio
from pathlib import Path
from urllib.parse import quote

import httpx

from src.state import GraphState, Scene


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
```

- [ ] **Step 4: Run tests — expect PASS**

```bash
pytest tests/test_agents.py -k "agent5" -v
```

- [ ] **Step 5: Commit**

```bash
git add src/agents/agent5_generate_images.py tests/test_agents.py
git commit -m "feat: agent5 fetch images from pollinations.ai"
```

---

## Task 9: Graph Assembly

**Files:**
- Create: `src/graph.py`
- Create: `tests/test_graph.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_graph.py
from src.graph import build_graph, route_after_agent4
from src.state import GraphState

def make_state(**kwargs) -> GraphState:
    base: GraphState = {
        "draft": "", "graphic_style": "", "is_create_image": False,
        "completed_script": "", "styled_script": "",
        "scenes": [], "scenes_with_prompts": [], "final_scenes": [],
    }
    base.update(kwargs)
    return base

def test_route_to_agent5_when_is_create_image_true():
    state = make_state(is_create_image=True)
    assert route_after_agent4(state) == "agent5_generate_images"

def test_route_to_end_when_is_create_image_false():
    from langgraph.graph import END
    state = make_state(is_create_image=False)
    assert route_after_agent4(state) == END

def test_graph_compiles():
    graph = build_graph()
    assert graph is not None

def test_graph_has_expected_nodes():
    graph = build_graph()
    node_names = set(graph.get_graph().nodes.keys())
    expected = {"agent1_analyze", "agent2_style", "agent3_split_scenes",
                "agent4_image_prompts", "agent5_generate_images"}
    assert expected.issubset(node_names)
```

- [ ] **Step 2: Run tests — expect FAIL**

```bash
pytest tests/test_graph.py -v
```

- [ ] **Step 3: Implement `src/graph.py`**

```python
"""
Screenplay agent LangGraph pipeline.

IMPORTANT: agent5_generate_images is async. Always use graph.ainvoke() — never
graph.invoke() — or the async node will fail at runtime.
"""
from langgraph.graph import StateGraph, START, END

from src.state import GraphState
from src.agents.agent1_analyze import agent1_analyze
from src.agents.agent2_style import agent2_style
from src.agents.agent3_split_scenes import agent3_split_scenes
from src.agents.agent4_image_prompts import agent4_image_prompts
from src.agents.agent5_generate_images import agent5_generate_images


def route_after_agent4(state: GraphState) -> str:
    return "agent5_generate_images" if state["is_create_image"] else END


def build_graph():
    builder = StateGraph(GraphState)

    builder.add_node("agent1_analyze", agent1_analyze)
    builder.add_node("agent2_style", agent2_style)
    builder.add_node("agent3_split_scenes", agent3_split_scenes)
    builder.add_node("agent4_image_prompts", agent4_image_prompts)
    builder.add_node("agent5_generate_images", agent5_generate_images)

    builder.add_edge(START, "agent1_analyze")
    builder.add_edge("agent1_analyze", "agent2_style")
    builder.add_edge("agent2_style", "agent3_split_scenes")
    builder.add_edge("agent3_split_scenes", "agent4_image_prompts")

    builder.add_conditional_edges(
        "agent4_image_prompts",
        route_after_agent4,
        {
            "agent5_generate_images": "agent5_generate_images",
            END: END,
        },
    )
    builder.add_edge("agent5_generate_images", END)

    return builder.compile()


graph = build_graph()
```

- [ ] **Step 4: Run tests — expect PASS**

```bash
pytest tests/test_graph.py -v
```
Expected: `4 passed`

- [ ] **Step 5: Commit**

```bash
git add src/graph.py tests/test_graph.py
git commit -m "feat: assemble langgraph pipeline with conditional routing"
```

---

## Task 10: CLI Entry Point

**Files:**
- Create: `src/main.py`
- Create: `tests/test_main.py`

- [ ] **Step 1: Write failing test**

```python
# tests/test_main.py
import subprocess
import sys

def test_cli_help_exits_zero():
    result = subprocess.run(
        [sys.executable, "-m", "src.main", "--help"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "--draft" in result.stdout
    assert "--style" in result.stdout
    assert "--create-images" in result.stdout
```

- [ ] **Step 2: Run test — expect FAIL**

```bash
pytest tests/test_main.py -v
```
Expected: `ModuleNotFoundError` or similar

- [ ] **Step 3: Implement `src/main.py`**

```python
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
    print(f"\n🎬 Running screenplay agent pipeline...")
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
```

- [ ] **Step 4: Run test — expect PASS**

```bash
pytest tests/test_main.py -v
```
Expected: `1 passed`

- [ ] **Step 5: Run all tests**

```bash
pytest tests/ -v
```
Expected: all tests pass

- [ ] **Step 6: Smoke test (requires `ANTHROPIC_API_KEY`)**

```bash
python -m src.main --draft "Một cô gái trẻ trở về quê hương sau 10 năm xa cách." --style "Cinematic Realism"
```
Expected: prints styled script + JSON scenes

- [ ] **Step 7: Commit**

```bash
git add src/main.py tests/test_main.py
git commit -m "feat: CLI entry point for screenplay agent pipeline"
```

---

## Task 11: Full Test Suite

- [ ] **Step 1: Run full test suite**

```bash
pytest tests/ -v --tb=short
```
Expected: all unit tests pass

- [ ] **Step 2: Verify graph visualization (optional)**

```python
# In a Python REPL:
from src.graph import graph
print(graph.get_graph().draw_ascii())
```

- [ ] **Step 3: Final commit**

```bash
git add .
git commit -m "chore: final review and cleanup"
```
