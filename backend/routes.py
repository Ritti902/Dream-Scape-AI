import logging
import os
import uuid
from pathlib import Path

import torch
from fastapi import APIRouter, BackgroundTasks, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse
from src.ai_core.paths import OUTPUT_ROOT

from schemas import (
    AnalyzeRequest,
    AnalyzeResponse,
    GenerateDreamRequest,
    GenerateDreamResponse,
    HealthResponse,
)

logger = logging.getLogger(__name__)
router = APIRouter()

APP_VERSION = os.getenv("APP_VERSION", "1.0.0")
OUTPUT_DIR = OUTPUT_ROOT

_job_status = {}


def _file_url(request: Request, rel_path: str) -> str:
    if not rel_path:
        return ""
    fname = Path(rel_path).name
    folder = Path(rel_path).parent.name
    return f"outputs/{folder}/{fname}"


@router.get("/health", response_model=HealthResponse, tags=["System"])
async def health_check():
    loaded = ["emotion-distilroberta"]
    try:
        import diffusers
        loaded.append("stable-diffusion")
    except ImportError:
        pass
    try:
        import audiocraft
        loaded.append("musicgen")
    except ImportError:
        pass

    return HealthResponse(
        status="ok",
        version=APP_VERSION,
        gpu_available=torch.cuda.is_available(),
        models_loaded=loaded,
    )


@router.post("/analyze", response_model=AnalyzeResponse, tags=["Analysis"])
async def analyze_text(body: AnalyzeRequest):
    try:
        from src.ai_core import emotion as emotion_module
        from src.ai_core import music_gen

        result = emotion_module.analyze(body.text)
        emotion = result["emotion"]

        art_style_map = {
            "sad": "painterly",
            "happy": "photorealistic",
            "fearful": "cyberpunk",
            "angry": "surrealist",
            "surprised": "watercolor",
            "neutral": "photorealistic",
        }

        return AnalyzeResponse(
            emotion=emotion,
            confidence=result["confidence"],
            themes=result["themes"],
            all_emotions=result["all_emotions"],
            suggested_art_style=art_style_map.get(emotion, "photorealistic"),
            music_prompt=music_gen.get_music_prompt(emotion),
        )
    except Exception as e:
        logger.exception("Analysis failed")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate", response_model=GenerateDreamResponse, tags=["Generation"])
async def generate_dream(body: GenerateDreamRequest, request: Request):
    try:
        from src.ai_core.pipeline import DreamRequest, get_pipeline

        pipeline = get_pipeline()

        dream_req = DreamRequest(
            text=body.text,
            art_style=body.art_style,
            animation_style=body.animation_style,
            image_steps=body.image_steps,
            image_cfg=body.image_cfg,
            video_duration=body.video_duration,
            seed=body.seed,
        )

        result = pipeline.run(dream_req)

        if result.error:
            raise HTTPException(status_code=500, detail=result.error)

        return GenerateDreamResponse(
            request_id=result.request_id,
            emotion=result.emotion,
            confidence=result.confidence,
            themes=result.themes,
            prompt=result.prompt,
            image_url=_file_url(request, result.image_path),
            video_url=_file_url(request, result.video_path),
            music_url=_file_url(request, result.music_path) if result.music_path else None,
            seed=result.seed,
            art_style=result.art_style,
            music_source=result.music_source,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Dream generation failed")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate/async", tags=["Generation"])
async def generate_dream_async(body: GenerateDreamRequest, background_tasks: BackgroundTasks):
    job_id = uuid.uuid4().hex[:12]
    _job_status[job_id] = {"status": "queued", "result": None, "error": None}

    def _run():
        from src.ai_core.pipeline import DreamRequest, get_pipeline
        _job_status[job_id]["status"] = "processing"
        try:
            pipeline = get_pipeline()
            req = DreamRequest(
                text=body.text,
                art_style=body.art_style,
                animation_style=body.animation_style,
                image_steps=body.image_steps,
                image_cfg=body.image_cfg,
                video_duration=body.video_duration,
                seed=body.seed,
                request_id=job_id,
            )
            result = pipeline.run(req)
            _job_status[job_id]["status"] = "done" if not result.error else "failed"
            _job_status[job_id]["result"] = result.__dict__
            _job_status[job_id]["error"] = result.error
        except Exception as e:
            _job_status[job_id]["status"] = "failed"
            _job_status[job_id]["error"] = str(e)

    background_tasks.add_task(_run)
    return JSONResponse({"job_id": job_id, "status": "queued"}, status_code=202)


@router.get("/jobs/{job_id}", tags=["Generation"])
async def get_job_status(job_id: str, request: Request):
    job = _job_status.get(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")

    response = {"job_id": job_id, "status": job["status"]}

    if job["status"] == "done" and job["result"]:
        r = job["result"]
        response["result"] = {
            "request_id": r.get("request_id"),
            "emotion": r.get("emotion"),
            "themes": r.get("themes"),
            "image_url": _file_url(request, r.get("image_path", "")),
            "video_url": _file_url(request, r.get("video_path", "")),
            "music_url": _file_url(request, r.get("music_path", "")) if r.get("music_path") else None,
            "seed": r.get("seed"),
        }
    elif job["status"] == "failed":
        response["error"] = job["error"]

    return JSONResponse(response)


@router.get("/outputs/{folder}/{filename}", tags=["Files"])
async def serve_output(folder: str, filename: str):
    allowed_folders = {"images", "videos", "music"}
    if folder not in allowed_folders:
        raise HTTPException(status_code=400, detail="Invalid folder")

    file_path = OUTPUT_DIR / folder / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(str(file_path))
