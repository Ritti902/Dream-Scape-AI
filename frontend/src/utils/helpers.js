const HISTORY_STORAGE_KEY = 'dreamscape-history-v2'

const EMOTION_META = {
  angry: {
    label: 'Anger',
    color: '#fb7185',
    description: 'High energy, intensity, and heat.',
  },
  fearful: {
    label: 'Fear',
    color: '#c084fc',
    description: 'Suspense, tension, and unease.',
  },
  fear: {
    label: 'Fear',
    color: '#c084fc',
    description: 'Suspense, tension, and unease.',
  },
  happy: {
    label: 'Joy',
    color: '#fbbf24',
    description: 'Brightness, lift, and momentum.',
  },
  neutral: {
    label: 'Neutral',
    color: '#7dd3fc',
    description: 'Balanced, reflective, and calm.',
  },
  peace: {
    label: 'Peace',
    color: '#34d399',
    description: 'Soft focus, stillness, and clarity.',
  },
  sad: {
    label: 'Sadness',
    color: '#93c5fd',
    description: 'Quiet, depth, and melancholy.',
  },
  surprise: {
    label: 'Surprise',
    color: '#f9a8d4',
    description: 'Lift, curiosity, and contrast.',
  },
  surprised: {
    label: 'Surprise',
    color: '#f9a8d4',
    description: 'Lift, curiosity, and contrast.',
  },
  wonder: {
    label: 'Wonder',
    color: '#67e8f9',
    description: 'Scale, awe, and dream logic.',
  },
}

function safeReadHistory() {
  try {
    const raw = localStorage.getItem(HISTORY_STORAGE_KEY)
    if (!raw) return []

    const parsed = JSON.parse(raw)
    return Array.isArray(parsed) ? parsed : []
  } catch {
    return []
  }
}

function safeWriteHistory(entries) {
  localStorage.setItem(HISTORY_STORAGE_KEY, JSON.stringify(entries))
}

export function formatDate(date) {
  try {
    return new Date(date).toLocaleString(undefined, {
      dateStyle: 'medium',
      timeStyle: 'short',
    })
  } catch {
    return 'Unknown date'
  }
}

export function truncate(text, limit = 120) {
  if (!text) return ''
  return text.length > limit ? `${text.slice(0, limit)}...` : text
}

export function toPercent(value) {
  const number = Number(value)
  if (!Number.isFinite(number) || number <= 0) return '0%'
  return `${Math.min(100, Math.max(0, number * 100)).toFixed(0)}%`
}

export function getEmotionMeta(key) {
  return EMOTION_META[key] || {
    label: key ? key[0].toUpperCase() + key.slice(1) : 'Unknown',
    color: '#7dd3fc',
    description: 'A custom emotion profile.',
  }
}

export function getThemeSummary(themes) {
  if (!Array.isArray(themes) || themes.length === 0) return 'No theme tags returned yet.'
  return themes.join(', ')
}

export function getDreamHistory() {
  return safeReadHistory().sort(
    (left, right) => new Date(right.created_at).getTime() - new Date(left.created_at).getTime(),
  )
}

export function saveDreamToHistory(text, result) {
  const entry = {
    request_id: result.request_id,
    created_at: new Date().toISOString(),
    text,
    note: '',
    emotion: result.emotion,
    confidence: result.confidence,
    themes: result.themes,
    prompt: result.prompt,
    image_url: result.image_url,
    video_url: result.video_url,
    music_url: result.music_url,
    seed: result.seed,
    art_style: result.art_style,
    music_source: result.music_source,
  }

  const history = getDreamHistory().filter((item) => item.request_id !== entry.request_id)
  safeWriteHistory([entry, ...history].slice(0, 30))
  return entry
}

export function updateDreamNote(requestId, note) {
  const history = getDreamHistory()
  const nextHistory = history.map((entry) =>
    entry.request_id === requestId ? { ...entry, note } : entry,
  )
  safeWriteHistory(nextHistory)
}

export function getEmotionCounts(entries) {
  return entries.reduce((counts, entry) => {
    const key = entry.emotion || 'neutral'
    counts[key] = (counts[key] || 0) + 1
    return counts
  }, {})
}

export function getDominantEmotion(entries) {
  const counts = getEmotionCounts(entries)
  const [emotion] = Object.entries(counts).sort((left, right) => right[1] - left[1])[0] || []
  return emotion || 'neutral'
}
