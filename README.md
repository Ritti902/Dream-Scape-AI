# DreamScape AI

DreamScape AI turns a short text prompt into a cinematic AI output. The app analyzes the emotion in the prompt, expands it into a richer creative direction, generates an image, adds music, and assembles a short dream-like video.

## What It Includes

- A React + Vite frontend for prompt entry, generation flow, and result viewing
- A FastAPI backend with sync and async generation endpoints
- AI pipeline modules for emotion detection, prompt building, image generation, music generation, and video creation
- Static serving for generated output files

## Tech Stack

- Frontend: React, Vite, Axios, React Router
- Backend: FastAPI, Uvicorn, Pydantic
- AI and media: PyTorch, Diffusers, Transformers, MoviePy

## Project Structure

```text
Dream-Scape-AI/
|-- backend/
|   |-- main.py
|   |-- routes.py
|   |-- schemas.py
|   `-- src/ai_core/
|-- frontend/
|   |-- src/
|   |-- package.json
|   `-- vite.config.js
|-- requirements.txt
`-- README.md
```

## How The Flow Works

1. The user enters a text prompt in the frontend.
2. The backend detects emotion and themes from the text.
3. The prompt builder expands that input into a generation-ready creative prompt.
4. The pipeline generates image, music, and video assets.
5. The frontend displays the generated results and links to output files.

## Quick Start

### Prerequisites

- Python 3.10+
- Node.js 18+
- A machine capable of running the listed AI dependencies

### 1. Clone the repository

```bash
git clone https://github.com/Ritti902/Dream-Scape-AI.git
cd Dream-Scape-AI
```

### 2. Install backend dependencies

```bash
pip install -r requirements.txt
```

### 3. Start the backend

Run this from the `backend/` folder:

```bash
python main.py
```

The backend defaults to `http://127.0.0.1:8000`.

### 4. Install frontend dependencies

Run this from the `frontend/` folder:

```bash
npm install
```

### 5. Start the frontend

```bash
npm run dev
```

The frontend is configured to call `http://127.0.0.1:8000/api/v1`.

## Environment Variables

Main backend settings:

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

## API Routes

- `GET /` returns basic service metadata
- `GET /api/v1/health` returns backend health and model availability
- `POST /api/v1/analyze` analyzes prompt emotion without generating assets
- `POST /api/v1/generate` runs the full generation pipeline
- `POST /api/v1/generate/async` starts generation in the background
- `GET /api/v1/jobs/{job_id}` checks async generation status
- `GET /outputs/{folder}/{filename}` serves generated files

## Output Files

- Generated media is written under `backend/outputs/`
- Output audio, image, and video artifacts are intentionally ignored by git

## Notes

- First-run model downloads can be large and slow
- Practical generation performance will be much better with a GPU
- The frontend lockfile is committed for reproducible installs

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE).
