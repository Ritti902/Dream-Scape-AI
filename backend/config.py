import os
from pathlib import Path
from functools import lru_cache


BASE_DIR = Path(__file__).resolve().parent


def _resolve_path(value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else BASE_DIR / path


class Settings:
    app_name = "DreamScape AI"
    app_version = "1.0.0"
    debug = False
    log_level = "INFO"
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    workers = 1
    cors_origins = ["http://localhost:3000", "http://localhost:5173"]
    openai_api_key = os.getenv("OPENAI_API_KEY", "")
    sd_model = os.getenv("SD_MODEL", "runwayml/stable-diffusion-v1-5")
    sd_steps = int(os.getenv("SD_STEPS", 30))
    sd_cfg = float(os.getenv("SD_CFG", 7.5))
    image_width = int(os.getenv("IMAGE_WIDTH", 768))
    image_height = int(os.getenv("IMAGE_HEIGHT", 512))
    music_duration = int(os.getenv("MUSIC_DURATION", 10))
    music_samples_dir = os.getenv("MUSIC_SAMPLES_DIR", "assets/music_samples")
    video_fps = int(os.getenv("VIDEO_FPS", 24))
    video_duration = int(os.getenv("VIDEO_DURATION", 8))
    output_dir = str(_resolve_path(os.getenv("OUTPUT_DIR", "outputs")))

    @property
    def output_images_dir(self):
        return Path(self.output_dir) / "images"

    @property
    def output_videos_dir(self):
        return Path(self.output_dir) / "videos"

    @property
    def output_music_dir(self):
        return Path(self.output_dir) / "music"

    def create_output_dirs(self):
        for d in [self.output_images_dir, self.output_videos_dir, self.output_music_dir]:
            d.mkdir(parents=True, exist_ok=True)


@lru_cache
def get_settings():
    return Settings()
