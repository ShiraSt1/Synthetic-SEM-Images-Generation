from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import os, io, requests, base64
from typing import List, Literal, Optional
from PIL import Image, ImageDraw

# Required ENV variables (no defaults)
LLAMA_BASE    = os.environ["LLAMA_BASE"]
LLAMA_APIKEY  = os.environ["LLAMA_APIKEY"]
NLP_BASE      = os.environ["NLP_BASE"]
NLP_APIKEY    = os.environ["NLP_APIKEY"]
IMAGE_URL     = os.environ["IMAGE_URL"]
IMAGE_APIKEY  = os.environ["IMAGE_APIKEY"]
TIMEOUT       = int(os.environ["TIMEOUT_SEC"])

# Fixed image size
FIXED_WIDTH  = 512
FIXED_HEIGHT = 512

# Mock mode configuration
MOCK_COUNT   = 2
MOCK_MIME    = "image/png"

app = FastAPI(title="Text→Embedding→Images Bridge")

class NLPParams(BaseModel):
    use_lemma: bool = True
    keep_pos: Optional[List[str]] = None
    lowercase: bool = True
    min_tokens: int = 1
    weighted: bool = False

class RequestBody(BaseModel):
    text: str
    source: Literal["llm", "nlp"]
    llm_model: Optional[str] = None
    nlp_params: Optional[NLPParams] = None
    image_url_override: Optional[str] = None

def embed_with_llm(text: str, model: str) -> List[float]:
    r = requests.post(
        f"{LLAMA_BASE}/embeddings",
        headers={"Authorization": f"Bearer {LLAMA_APIKEY}", "Content-Type": "application/json"},
        json={"model": model, "input": [text]},
        timeout=TIMEOUT,
    )
    if r.status_code != 200:
        raise HTTPException(502, f"llama-server embeddings error: {r.text}")
    return r.json()["data"][0]["embedding"]

def embed_with_nlp(text: str, params: Optional[NLPParams]) -> List[float]:
    body = {"text": text}
    if params is not None:
        body.update(params.dict())
    r = requests.post(
        f"{NLP_BASE}/embed",
        headers={"Content-Type": "application/json", "X-API-Key": NLP_APIKEY},
        json=body,
        timeout=TIMEOUT,
    )
    if r.status_code != 200:
        raise HTTPException(502, f"NLP embed error: {r.text}")
    return r.json().get("vector")

def png_bytes(label: str) -> bytes:
    img = Image.new("RGB", (FIXED_WIDTH, FIXED_HEIGHT), (32, 32, 48))
    d = ImageDraw.Draw(img)
    d.text((10, 10), label, fill=(220, 220, 240))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()

def to_b64(data: bytes) -> str:
    return base64.b64encode(data).decode("ascii")

def mock_images(text: str) -> JSONResponse:
    imgs = []
    for i in range(MOCK_COUNT):
        raw = png_bytes(f"MOCK {i+1}/{MOCK_COUNT}\n{FIXED_WIDTH}x{FIXED_HEIGHT}\n{text[:40]}")
        imgs.append(to_b64(raw))
    return JSONResponse({"images_base64": imgs, "mime": MOCK_MIME})

def send_to_image_server(embedding: List[float], image_url_override: Optional[str], text_for_mock: str) -> JSONResponse:
    url_sel = (image_url_override or IMAGE_URL or "").lower()

    # MOCK mode → return generated placeholder images
    if url_sel.startswith("mock") or url_sel == "":
        return mock_images(text_for_mock)

    # Normal mode → forward embedding to image server
    headers = {"Content-Type": "application/json"}
    if IMAGE_APIKEY:
        headers["Authorization"] = f"Bearer {IMAGE_APIKEY}"  # Skip if empty

    payload = {"embedding": embedding, "width": FIXED_WIDTH, "height": FIXED_HEIGHT}
    r = requests.post(url_sel, headers=headers, json=payload, timeout=TIMEOUT)

    # Interpret image server response
    ctype = r.headers.get("Content-Type", "")
    # 1) JSON response with base64 images
    if ctype.startswith("application/json"):
        try:
            j = r.json()
            if "images_base64" in j and isinstance(j["images_base64"], list):
                return JSONResponse(j, status_code=r.status_code)
            if "image_base64" in j:
                return JSONResponse({"images_base64": [j["image_base64"]], "mime": j.get("mime", "image/png")}, status_code=r.status_code)
        except Exception:
            pass

    # 2) Raw binary image → wrap as base64
    if r.status_code == 200 and (ctype.startswith("image/") or ctype.startswith("application/octet-stream")):
        b64 = to_b64(r.content)
        return JSONResponse({"images_base64": [b64], "mime": ctype if ctype.startswith("image/") else "image/png"})

    # 3) Otherwise → return error
    raise HTTPException(502, f"image server error: {r.text}")

@app.post("/v1/text-to-image")
def text_to_image(req: RequestBody):
    if req.source == "llm":
        if not req.llm_model:
            raise HTTPException(400, "llm_model is required when source='llm'")
        embedding = embed_with_llm(req.text, req.llm_model)
    elif req.source == "nlp":
        embedding = embed_with_nlp(req.text, req.nlp_params)
    else:
        raise HTTPException(400, "source must be 'llm' or 'nlp'")

    return send_to_image_server(embedding, req.image_url_override, req.text)