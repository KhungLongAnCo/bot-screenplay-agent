# Screenplay Agent Flow

Hệ thống multi-agent tự động hoá quy trình phát triển kịch bản điện ảnh — từ một ý tưởng thô đến bộ scene hoàn chỉnh kèm hình ảnh minh hoạ.

---

## Kiến trúc tổng quan

```
[User Draft Input]
        │
        ▼
┌──────────────┐
│   Agent 1    │  Phân tích & hoàn thiện kịch bản
└──────┬───────┘
       │
       ▼
┌──────────────┐
│   Agent 2    │  Viết lại theo phong cách điện ảnh (có reference script)
└──────┬───────┘
       │
       ▼
┌──────────────┐
│   Agent 3    │  Phân tách thành các scene riêng biệt
└──────┬───────┘
       │
       ▼
┌──────────────┐
│   Agent 4    │  Tạo image prompt cho từng scene
└──────┬───────┘
       │
    isCreateImage?
      /        \
    YES         NO
     │           │
     ▼           ▼
┌──────────┐  [SKIP]
│  Agent 5 │
└──────┬───┘
       │
       ▼
[Scene Table: sceneScript | imagePrompt | imageUrl]
```

---

## Chi tiết từng Agent

### Agent 1 — Phân tích & hoàn thiện kịch bản

**Mục đích:** Nhận input thô từ người dùng (có thể chỉ là vài dòng ý tưởng) và phát triển thành kịch bản có cấu trúc.

**System prompt định hướng:**
- Phân tích chủ đề chính, nhân vật, cung bậc cảm xúc
- Xây dựng cấu trúc 3 hồi (setup → confrontation → resolution)
- Phát triển 3–5 phân cảnh chính
- Giữ nguyên tinh thần draft gốc

**Input:** Draft text của người dùng  
**Output:** Kịch bản hoàn chỉnh dạng văn bản (chưa có format)

---

### Agent 2 — Viết lại theo phong cách điện ảnh

**Mục đích:** Nâng cấp ngôn ngữ và cấu trúc kịch bản theo đúng chuẩn format điện ảnh chuyên nghiệp.

**Kỹ thuật đặc biệt — Reference Script Injection:**  
Một đoạn kịch bản mẫu chất lượng cao được nhúng trực tiếp vào system prompt để agent học phong cách:
- Cách dùng hình ảnh mạnh, súc tích
- Nhịp điệu hành động và đối thoại
- Chỉ dẫn cảnh ngắn gọn nhưng giàu hình ảnh
- Cảm xúc được gợi qua chi tiết, không tường thuật trực tiếp

**Format output chuẩn:**
```
INT/EXT. ĐỊA ĐIỂM - THỜI GIAN
[Hành động]

TÊN NHÂN VẬT
(chỉ dẫn diễn xuất)
Thoại...
```

**Input:** Kịch bản từ Agent 1 + Reference script  
**Output:** Kịch bản định dạng chuẩn điện ảnh

---

### Agent 3 — Phân tách thành các Scene

**Mục đích:** Tách kịch bản liên tục thành các scene object độc lập, chuẩn bị cho pipeline downstream.

**Logic phân tách:**
- Mỗi thẻ `INT.` / `EXT.` = một scene mới
- Giữ nguyên toàn bộ nội dung gốc trong `sceneScript`
- Tối thiểu 3, tối đa 8 scenes

**Output schema (JSON array):**
```json
[
  {
    "sceneNumber": 1,
    "title": "Tên ngắn gọn",
    "location": "INT/EXT. ĐỊA ĐIỂM - THỜI GIAN",
    "sceneScript": "Toàn bộ nội dung scene..."
  }
]
```

**Input:** Kịch bản từ Agent 2  
**Output:** JSON array các scene objects

---

### Agent 4 — Tạo Image Prompt

**Mục đích:** Với mỗi scene, tạo một visual prompt chi tiết bằng tiếng Anh để đưa vào AI image generation.

**Cấu trúc prompt được tạo ra:**
1. **Phong cách đồ hoạ** (inject từ user selection)
2. **Góc máy & ánh sáng** — wide shot, close-up, golden hour, v.v.
3. **Nhân vật** — ngoại hình, trang phục, cảm xúc
4. **Môi trường** — địa điểm, thời gian, bầu không khí
5. Độ dài tối ưu: 50–80 từ tiếng Anh

**Graphic style presets:**
| Label | Giá trị inject vào prompt |
|---|---|
| Cinematic Realism | `cinematic realism, dramatic lighting, photorealistic, 8k film still` |
| Anime / Ghibli | `anime style, cel shading, Studio Ghibli inspired, vibrant colors` |
| Watercolor | `watercolor illustration, soft edges, painterly, editorial illustration` |
| Graphic Novel | `graphic novel, bold ink lines, high contrast, comic book panels` |
| Dark Fantasy | `dark fantasy, digital painting, atmospheric, dramatic shadows, concept art` |
| Vintage Film | `vintage film photography, 35mm grain, muted tones, 1970s aesthetic` |

**Output schema:**
```json
[
  {
    "sceneNumber": 1,
    "title": "...",
    "location": "...",
    "sceneScript": "...",
    "imagePrompt": "cinematic realism, dramatic lighting..."
  }
]
```

---

### Agent 5 — Generate Hình ảnh *(tuỳ chọn)*

**Mục đích:** Tạo URL ảnh minh hoạ cho từng scene dựa trên prompt đã tạo.

**Điều kiện chạy:** Chỉ kích hoạt khi `isCreateImage = true`. Nếu `false`, agent bị skip hoàn toàn và cột ảnh bị ẩn khỏi UI.

**Cơ chế hiện tại:**  
Sử dụng **Pollinations.ai** — free public API, không cần key:
```
https://image.pollinations.ai/prompt/{encoded_prompt}?width=768&height=432&nologo=true&seed={n}
```

**Output schema — object cuối cùng:**
```json
{
  "sceneNumber": 1,
  "title": "Tên scene",
  "location": "INT/EXT. ...",
  "sceneScript": "Nội dung scene...",
  "imagePrompt": "cinematic realism, ...",
  "imageUrl": "https://image.pollinations.ai/prompt/..."
}
```

---

## Công nghệ sử dụng

### Frontend
| Thành phần | Công nghệ |
|---|---|
| Giao diện | HTML5 / CSS3 / Vanilla JS (single-file) |
| Font | Bebas Neue (display) · DM Sans (body) · DM Mono (code/data) |
| Theme | Dark UI — transparent bg, CSS custom properties |
| State management | DOM mutation trực tiếp (không dùng framework) |

### AI / LLM — LangGraph
| Thành phần | Công nghệ |
|---|---|
| Orchestration | [LangGraph](https://langchain-ai.github.io/langgraph/) (Python) |
| Model | `claude-sonnet-4-20250514` qua `langchain-anthropic` |
| Structured output | `PydanticOutputParser` + `with_structured_output()` |
| Graph runtime | `StateGraph` + `TypedDict` state |
| Conditional edge | `isCreateImage` → route đến Agent 5 hoặc `END` |
| Serving | LangGraph API Server (FastAPI-compatible) |

### Image Generation
| Thành phần | Công nghệ |
|---|---|
| Provider | [Pollinations.ai](https://pollinations.ai) (demo) |
| Protocol | HTTP GET với encoded prompt trong URL |
| Resolution | 768 × 432 px (16:9) |
| Lazy loading | `img.onload` / `img.onerror` callbacks |

---

## LangGraph — Thiết kế hệ thống Agents

### Tại sao LangGraph?

LangGraph mô hình hoá pipeline multi-agent như một **directed graph** — mỗi agent là một node, luồng dữ liệu là edge. So với sequential API call thủ công:

| | Sequential thủ công | LangGraph |
|---|---|---|
| Conditional routing | `if/else` trong JS | Conditional edge khai báo rõ ràng |
| Shared state | Biến JS truyền tay | `TypedDict` state tập trung |
| Retry / error handling | Try-catch từng chỗ | Node-level retry policy |
| Observability | `console.log` | LangSmith trace tích hợp sẵn |
| Human-in-the-loop | Không có | `interrupt_before` / `interrupt_after` |
| Parallel execution | `Promise.all` thủ công | `Send()` API built-in |

---

### State Schema

Toàn bộ pipeline chia sẻ một `GraphState` duy nhất — mỗi node đọc và ghi vào đây:

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
    # Input từ user
    draft: str
    graphic_style: str
    is_create_image: bool

    # Output tích luỹ qua từng node
    completed_script: str       # Agent 1
    styled_script: str          # Agent 2
    scenes: List[Scene]         # Agent 3
    scenes_with_prompts: List[Scene]   # Agent 4
    final_scenes: List[Scene]   # Agent 5 hoặc copy từ Agent 4
```

---

### Graph Definition

```python
from langgraph.graph import StateGraph, END
from langchain_anthropic import ChatAnthropic

llm = ChatAnthropic(model="claude-sonnet-4-20250514", max_tokens=3000)

# ── Khai báo graph ──────────────────────────────────────────
builder = StateGraph(GraphState)

# Đăng ký các nodes
builder.add_node("agent1_analyze",       agent1_analyze)
builder.add_node("agent2_style",         agent2_style)
builder.add_node("agent3_split_scenes",  agent3_split_scenes)
builder.add_node("agent4_image_prompts", agent4_image_prompts)
builder.add_node("agent5_generate_images", agent5_generate_images)

# ── Edges tuyến tính ────────────────────────────────────────
builder.set_entry_point("agent1_analyze")
builder.add_edge("agent1_analyze",       "agent2_style")
builder.add_edge("agent2_style",         "agent3_split_scenes")
builder.add_edge("agent3_split_scenes",  "agent4_image_prompts")

# ── Conditional edge tại Agent 4 ───────────────────────────
def route_after_agent4(state: GraphState) -> str:
    return "agent5_generate_images" if state["is_create_image"] else END

builder.add_conditional_edges(
    "agent4_image_prompts",
    route_after_agent4,
    {
        "agent5_generate_images": "agent5_generate_images",
        END: END
    }
)

builder.add_edge("agent5_generate_images", END)

graph = builder.compile()
```

---

### Node Implementations

**Agent 1 — Phân tích & hoàn thiện**

```python
def agent1_analyze(state: GraphState) -> GraphState:
    prompt = ChatPromptTemplate.from_messages([
        ("system", AGENT1_SYSTEM_PROMPT),
        ("human", "KỊCH BẢN DRAFT:\n{draft}")
    ])
    chain = prompt | llm | StrOutputParser()
    result = chain.invoke({"draft": state["draft"]})
    return {"completed_script": result}
```

**Agent 2 — Viết lại theo phong cách**

```python
REFERENCE_SCRIPT = """..."""  # Kịch bản mẫu nhúng cứng

def agent2_style(state: GraphState) -> GraphState:
    prompt = ChatPromptTemplate.from_messages([
        ("system", AGENT2_SYSTEM_PROMPT.format(reference=REFERENCE_SCRIPT)),
        ("human", "{completed_script}")
    ])
    chain = prompt | llm | StrOutputParser()
    result = chain.invoke({"completed_script": state["completed_script"]})
    return {"styled_script": result}
```

**Agent 3 — Phân tách scenes (Structured Output)**

```python
from langchain_core.output_parsers import PydanticOutputParser

parser = PydanticOutputParser(pydantic_object=List[Scene])

def agent3_split_scenes(state: GraphState) -> GraphState:
    # Dùng with_structured_output để đảm bảo JSON hợp lệ
    structured_llm = llm.with_structured_output(List[Scene])
    prompt = ChatPromptTemplate.from_messages([
        ("system", AGENT3_SYSTEM_PROMPT),
        ("human", "{styled_script}")
    ])
    chain = prompt | structured_llm
    scenes = chain.invoke({"styled_script": state["styled_script"]})
    return {"scenes": scenes}
```

**Agent 4 — Tạo image prompts (Map over scenes)**

```python
def agent4_image_prompts(state: GraphState) -> GraphState:
    # Chạy song song trên từng scene với Send() API
    # (xem phần Parallel Execution bên dưới)
    scenes_with_prompts = []
    for scene in state["scenes"]:
        prompt_text = generate_image_prompt(
            scene=scene,
            graphic_style=state["graphic_style"],
            llm=llm
        )
        scenes_with_prompts.append(
            scene.model_copy(update={"image_prompt": prompt_text})
        )
    return {"scenes_with_prompts": scenes_with_prompts}
```

**Agent 5 — Generate hình ảnh**

```python
import httpx

async def agent5_generate_images(state: GraphState) -> GraphState:
    final_scenes = []
    async with httpx.AsyncClient() as client:
        tasks = [
            fetch_image(client, scene)
            for scene in state["scenes_with_prompts"]
        ]
        final_scenes = await asyncio.gather(*tasks)
    return {"final_scenes": final_scenes}

async def fetch_image(client, scene: Scene) -> Scene:
    url = (
        f"https://image.pollinations.ai/prompt/"
        f"{httpx.QueryParams({'prompt': scene.image_prompt})}"
        f"?width=768&height=432&nologo=true&seed={scene.scene_number * 42}"
    )
    # Lưu ảnh xuống local folder
    save_path = Path(f"output/scenes/scene_{scene.scene_number:02d}.jpg")
    response = await client.get(url)
    save_path.write_bytes(response.content)
    return scene.model_copy(update={"image_url": str(save_path)})
```

---

### Graph Visualization

```
[START]
   │
   ▼
agent1_analyze
   │
   ▼
agent2_style
   │
   ▼
agent3_split_scenes
   │
   ▼
agent4_image_prompts
   │
   ├── is_create_image = True ──▶ agent5_generate_images ──▶ [END]
   │
   └── is_create_image = False ─────────────────────────────▶ [END]
```

---

### Parallel Image Generation (tuỳ chọn nâng cao)

Thay vì loop tuần tự, dùng `Send()` API để fan-out mỗi scene thành node song song:

```python
from langgraph.types import Send

# Sub-graph xử lý 1 scene
def generate_single_image(state: dict) -> dict:
    scene = state["scene"]
    # ... generate image ...
    return {"processed_scene": scene}

# Fan-out node
def fan_out_scenes(state: GraphState):
    return [
        Send("generate_single_image", {"scene": s})
        for s in state["scenes_with_prompts"]
    ]

builder.add_conditional_edges("agent4_image_prompts", fan_out_scenes)
builder.add_node("generate_single_image", generate_single_image)
```

Tất cả N scenes được generate **đồng thời**, giảm latency từ `N × t` xuống `~t`.

---

### Observability với LangSmith

```python
import os
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = "screenplay-agent-flow"
os.environ["LANGCHAIN_API_KEY"] = "ls__..."

# Toàn bộ graph execution được trace tự động:
# - Token usage từng node
# - Latency từng bước
# - Input/output tại mỗi agent
# - Error với full stack trace
result = await graph.ainvoke({
    "draft": user_draft,
    "graphic_style": selected_style,
    "is_create_image": True
})
```

---

## Data flow chi tiết

```
User Input (string)
    │
    ├─ [Agent 1] → completedScript (string)
    │
    ├─ [Agent 2] → styledScript (string)
    │
    ├─ [Agent 3] → scenes[] (JSON)
    │     { sceneNumber, title, location, sceneScript }
    │
    ├─ [Agent 4] → scenes[] (JSON, enriched)
    │     { ...prev, imagePrompt }
    │
    └─ [Agent 5, nếu enabled] → scenes[] (JSON, final)
          { ...prev, imageUrl }
```

---

## Xử lý lỗi & Edge cases

**JSON parsing resilient:** Agent 3 và 4 trả về JSON — parser thử 2 lần: parse thẳng → fallback regex extract `[...]` block.

**Image load fallback:** Nếu Pollinations trả về lỗi, card hiển thị message thay vì broken image.

**isCreateImage = false:** Agent 5 không chạy, cột ảnh ẩn hoàn toàn khỏi table header và scene cards. Step 5 trong pipeline hiển thị mờ (opacity 0.35).

**Token budget:**
| Agent | max_tokens |
|---|---|
| Agent 1 | 3000 |
| Agent 2 | 3000 |
| Agent 3 | 2500 |
| Agent 4 | 3000 |

---

## Hướng phát triển tiếp theo

**Image generation production-ready:**  
Thay Pollinations.ai bằng Replicate API (`black-forest-labs/flux-schnell`) hoặc OpenAI DALL·E 3 để có chất lượng cao hơn và SLA ổn định.

**Parallel agent execution:**  
Agent 5 có thể generate song song N ảnh cùng lúc thay vì tuần tự — dùng `Promise.all()`.

**Export:**  
Thêm nút export ra PDF / CSV / Final Draft format.

**Streaming response:**  
Dùng Anthropic streaming API để agent output hiển thị real-time, cải thiện UX đáng kể.

**Agent memory / context carry-over:**  
Hiện tại mỗi agent nhận nguyên output của agent trước. Có thể tối ưu bằng cách chỉ truyền summary + relevant context để tiết kiệm token.
