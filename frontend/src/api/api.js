import axios from 'axios'

const API_BASE_URL = 'http://127.0.0.1:8000/api/v1'

const client = axios.create({
  baseURL: API_BASE_URL,
  timeout: 300_000,
  headers: {
    'Content-Type': 'application/json',
  },
})

function getErrorMessage(error, fallback) {
  return error?.response?.data?.detail || error?.message || fallback
}

export async function checkHealth() {
  try {
    const { data } = await client.get('/health')
    return { ok: true, data }
  } catch (error) {
    return {
      ok: false,
      error: getErrorMessage(error, 'Backend is unavailable right now.'),
    }
  }
}

export async function analyseEmotion(text) {
  try {
    const { data } = await client.post('/analyze', { text })
    return data
  } catch (error) {
    throw new Error(getErrorMessage(error, 'Unable to analyze this prompt.'))
  }
}

export async function startDream(payload) {
  const body = {
    text: payload.text,
    art_style: payload.artStyle,
    animation_style: payload.animationStyle || null,
    image_steps: payload.imageSteps,
    image_cfg: payload.imageCfg,
    video_duration: payload.videoDuration,
    seed: payload.seed ?? null,
  }

  try {
    const { data } = await client.post('/generate', body)
    return data
  } catch (error) {
    throw new Error(getErrorMessage(error, 'Dream generation failed.'))
  }
}

export default client
