# DreamScape AI

DreamScape AI turns a text prompt into a generated visual, soundtrack, and short cinematic output. The project combines a React frontend with a FastAPI backend and AI generation modules for emotion analysis, prompt building, image creation, music generation, and video assembly.

## Stack

- Frontend: React, Vite, Axios, React Router
- Backend: FastAPI, Uvicorn, Pydantic
- AI and media: PyTorch, Diffusers, Transformers, MoviePy

## Project Layout

```text
Dream-Scape-AI/
|-- backend/
|   |-- main.py
|   |-- routes.py
|   `-- src/ai_core/
|-- frontend/
|   |-- src/
|   `-- package.json
|-- requirements.txt
`-- README.md
```

## Features

- Analyze prompt emotion and themes
- Suggest an art style based on emotion
- Generate image, music, and video outputs
- Expose synchronous and async generation endpoints
- Serve generated files from the backend

## Local Setup

### Backend

1. Create and activate a Python virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Start the API from `backend/`:

```bash
python main.py
```

The backend runs on `http://127.0.0.1:8000` by default.

### Frontend

1. Install frontend dependencies from `frontend/`:

```bash
npm install
```

2. Start the Vite dev server:

```bash
npm run dev
```

The frontend expects the API at `http://127.0.0.1:8000/api/v1`.

## Environment Variables

These are the main backend settings used by the project:

```env
OPENAI_API_KEY=
HOST=0.0.0.0
PORT=8000
SD_MODEL=runwayml/stable-diffusion-v1-5
SD_STEPS=30
SD_CFG=7.5
IMAGE_WIDTH=768
IMAGE_HEIGHT=512
MUSIC_DURATION=10
VIDEO_DURATION=8
OUTPUT_DIR=outputs
```

## API Endpoints

- `GET /` for service info
- `GET /api/v1/health` for backend health
- `POST /api/v1/analyze` for emotion analysis
- `POST /api/v1/generate` for direct generation
- `POST /api/v1/generate/async` for queued generation
- `GET /api/v1/jobs/{job_id}` for async job status

## Notes

- Generated media is written under `backend/outputs/`.
- Heavy AI dependencies may require a capable GPU for practical runtimes.
- The repo includes the frontend lockfile for reproducible installs.

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE).
