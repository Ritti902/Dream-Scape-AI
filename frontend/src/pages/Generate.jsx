import { useEffect, useState } from 'react'
import { analyseEmotion } from '../api/api'
import ResultCard from '../components/ResultCard'
import StepProgress from '../components/StepProgress'
import useDream from '../hooks/useDream'
import { getEmotionMeta, getThemeSummary, toPercent } from '../utils/helpers'

const EXAMPLES = [
  'I feel lost in an endless ocean of silence with only distant city lights.',
  'A bright rush of joy dancing across a skyline at sunrise.',
  'I am floating through cosmic dust, curious and overwhelmed by wonder.',
]

const ART_STYLES = [
  { value: 'photorealistic', label: 'Photorealistic' },
  { value: 'surrealist', label: 'Surrealist' },
  { value: 'painterly', label: 'Painterly' },
  { value: 'anime', label: 'Anime' },
  { value: 'cyberpunk', label: 'Cyberpunk' },
  { value: 'van_gogh', label: 'Van Gogh' },
  { value: 'watercolor', label: 'Watercolor' },
]

const ANIMATION_STYLES = [
  { value: '', label: 'Auto' },
  { value: 'zoom_in', label: 'Zoom In' },
  { value: 'zoom_out', label: 'Zoom Out' },
  { value: 'pan_left', label: 'Pan Left' },
  { value: 'pan_right', label: 'Pan Right' },
  { value: 'ken_burns', label: 'Ken Burns' },
  { value: 'pulse', label: 'Pulse' },
]

function getOptionLabel(options, value, fallback) {
  return options.find((option) => option.value === value)?.label || fallback
}

export default function Generate() {
  const { currentStep, error, generate, progress, reset, result, savedEntry, status } = useDream()
  const [text, setText] = useState('')
  const [submittedText, setSubmittedText] = useState('')
  const [artStyle, setArtStyle] = useState('photorealistic')
  const [artStyleTouched, setArtStyleTouched] = useState(false)
  const [animationStyle, setAnimationStyle] = useState('')
  const [duration, setDuration] = useState(8)
  const [steps, setSteps] = useState(30)
  const [cfg, setCfg] = useState(7.5)
  const [seed, setSeed] = useState('')
  const [analysis, setAnalysis] = useState(null)
  const [analysisError, setAnalysisError] = useState('')
  const [analysisLoading, setAnalysisLoading] = useState(false)

  useEffect(() => {
    if (text.trim().length < 5) {
      setAnalysis(null)
      setAnalysisError('')
      setAnalysisLoading(false)
      return undefined
    }

    let active = true
    const timeoutId = window.setTimeout(async () => {
      setAnalysisLoading(true)
      setAnalysisError('')

      try {
        const response = await analyseEmotion(text.trim())
        if (!active) return

        setAnalysis(response)

        if (!artStyleTouched && response.suggested_art_style) {
          setArtStyle(response.suggested_art_style)
        }
      } catch (requestError) {
        if (active) {
          setAnalysisError(requestError.message || 'Unable to analyze the prompt right now.')
        }
      } finally {
        if (active) {
          setAnalysisLoading(false)
        }
      }
    }, 450)

    return () => {
      active = false
      window.clearTimeout(timeoutId)
    }
  }, [artStyleTouched, text])

  const emotionMeta = getEmotionMeta(result?.emotion || analysis?.emotion || 'neutral')
  const isProcessing = status === 'processing'
  const promptLength = text.trim().length
  const selectedArtStyle = getOptionLabel(ART_STYLES, artStyle, 'Custom style')
  const selectedAnimationStyle = getOptionLabel(ANIMATION_STYLES, animationStyle, 'Auto motion')

  function handleSubmit(event) {
    event.preventDefault()
    if (!text.trim() || isProcessing) return

    setSubmittedText(text.trim())
    generate({
      text: text.trim(),
      artStyle,
      animationStyle,
      imageSteps: steps,
      imageCfg: cfg,
      videoDuration: duration,
      seed: seed === '' ? undefined : Number(seed),
    })
  }

  function handleReset() {
    reset()
    setText('')
    setSubmittedText('')
    setArtStyle('photorealistic')
    setArtStyleTouched(false)
    setAnimationStyle('')
    setDuration(8)
    setSteps(30)
    setCfg(7.5)
    setSeed('')
    setAnalysis(null)
    setAnalysisError('')
  }

  return (
    <div className="page">
      <section className="section-heading page-heading animate-fade-up">
        <div>
          <div className="eyebrow-row">
            <p className="section-label">Studio</p>
            <span className="inline-badge">Minimal dark workspace</span>
          </div>
          <h1 className="page-title">Generate a dream sequence</h1>
        </div>
        <p className="page-copy">
          Write the feeling, refine the render profile, and launch a polished generation flow with live mood
          analysis, cleaner controls, and faster visual scanning.
        </p>
      </section>

      <div className="studio-grid">
        <form className="glass-card studio-form animate-fade-up delay-100" onSubmit={handleSubmit}>
          <div className="surface-banner">
            <div>
              <span className="metric-title">Session brief</span>
              <strong>{promptLength > 0 ? `${promptLength} characters ready` : 'Start with a feeling'}</strong>
            </div>
            <div className="pill-row">
              <span className="dw-chip">{selectedArtStyle}</span>
              <span className="dw-chip">{selectedAnimationStyle}</span>
              <span className="dw-chip">{duration}s scene</span>
            </div>
          </div>

          <div className="section-block">
            <div className="section-block-header">
              <div>
                <p className="section-label">Prompt</p>
                <h2>Describe the feeling you want to render</h2>
              </div>
              <span className="tiny-note">{promptLength > 0 ? `${promptLength} chars` : 'Minimum 5 chars'}</span>
            </div>

            <textarea
              className="dw-textarea"
              rows={7}
              value={text}
              onChange={(event) => setText(event.target.value)}
              placeholder="Example: A cold blue dream of grief on an empty street at 3am."
              disabled={isProcessing}
            />

            <div className="example-list">
              {EXAMPLES.map((example) => (
                <button
                  key={example}
                  type="button"
                  className="example-chip"
                  onClick={() => setText(example)}
                  disabled={isProcessing}
                >
                  {example}
                </button>
              ))}
            </div>
          </div>

          <div className="section-block">
            <div className="section-block-header">
              <div>
                <p className="section-label">Settings</p>
                <h2>Match the backend request exactly</h2>
              </div>
            </div>

            <div className="form-grid">
              <label className="form-field">
                <span className="field-label">Art style</span>
                <select
                  className="dw-select"
                  value={artStyle}
                  onChange={(event) => {
                    setArtStyle(event.target.value)
                    setArtStyleTouched(true)
                  }}
                  disabled={isProcessing}
                >
                  {ART_STYLES.map((option) => (
                    <option key={option.value} value={option.value}>
                      {option.label}
                    </option>
                  ))}
                </select>
              </label>

              <label className="form-field">
                <span className="field-label">Animation style</span>
                <select
                  className="dw-select"
                  value={animationStyle}
                  onChange={(event) => setAnimationStyle(event.target.value)}
                  disabled={isProcessing}
                >
                  {ANIMATION_STYLES.map((option) => (
                    <option key={option.value || 'auto'} value={option.value}>
                      {option.label}
                    </option>
                  ))}
                </select>
              </label>

              <label className="form-field">
                <span className="field-label">Video duration</span>
                <div className="range-row">
                  <input
                    type="range"
                    min="3"
                    max="30"
                    value={duration}
                    onChange={(event) => setDuration(Number(event.target.value))}
                    disabled={isProcessing}
                  />
                  <strong>{duration}s</strong>
                </div>
              </label>

              <label className="form-field">
                <span className="field-label">Image steps</span>
                <div className="range-row">
                  <input
                    type="range"
                    min="10"
                    max="100"
                    value={steps}
                    onChange={(event) => setSteps(Number(event.target.value))}
                    disabled={isProcessing}
                  />
                  <strong>{steps}</strong>
                </div>
              </label>

              <label className="form-field">
                <span className="field-label">Guidance scale</span>
                <div className="range-row">
                  <input
                    type="range"
                    min="1"
                    max="20"
                    step="0.5"
                    value={cfg}
                    onChange={(event) => setCfg(Number(event.target.value))}
                    disabled={isProcessing}
                  />
                  <strong>{cfg.toFixed(1)}</strong>
                </div>
              </label>

              <label className="form-field">
                <span className="field-label">Seed</span>
                <input
                  className="dw-input"
                  type="number"
                  min="0"
                  value={seed}
                  onChange={(event) => setSeed(event.target.value)}
                  placeholder="Leave blank for random"
                  disabled={isProcessing}
                />
              </label>
            </div>

            <div className="inline-actions">
              <button className="btn-primary" type="submit" disabled={!text.trim() || isProcessing}>
                {isProcessing ? 'Generating dream' : 'Generate dream'}
              </button>
              <button className="btn-secondary" type="button" onClick={handleReset} disabled={isProcessing}>
                Reset
              </button>
            </div>
          </div>

          {error && <div className="error-banner">{error}</div>}
        </form>

        <aside className="studio-sidebar stack-lg animate-fade-up delay-200">
          <div className="glass-card analysis-panel">
            <div className="section-block-header">
              <div>
                <p className="section-label">Live analysis</p>
                <h2>Backend mood preview</h2>
              </div>
              <span className="inline-badge inline-badge-muted">
                {analysisLoading ? 'Analyzing' : analysis ? 'Synced' : 'Waiting for prompt'}
              </span>
            </div>

            <div className="emotion-hero">
              <span className="emotion-swatch" style={{ backgroundColor: emotionMeta.color }} />
              <div>
                <h3>{emotionMeta.label}</h3>
                <p>{emotionMeta.description}</p>
              </div>
            </div>

            <div className="metric-row">
              <div>
                <span className="metric-title">Confidence</span>
                <strong>{analysis ? toPercent(analysis.confidence) : '0%'}</strong>
              </div>
              <div>
                <span className="metric-title">Suggested style</span>
                <strong>{analysis?.suggested_art_style?.replace(/_/g, ' ') || artStyle.replace(/_/g, ' ')}</strong>
              </div>
            </div>

            <div className="prompt-box">
              <strong>Theme summary</strong>
              <p>{analysis ? getThemeSummary(analysis.themes) : 'Type a prompt to see mood tags here.'}</p>
            </div>

            <div className="pill-row">
              {(analysis?.themes || []).length > 0 ? (
                analysis.themes.map((theme) => (
                  <span key={theme} className="dw-chip">
                    {theme}
                  </span>
                ))
              ) : (
                <span className="tiny-note">Theme tags appear here after the prompt is analyzed.</span>
              )}
            </div>

            <div className="prompt-box">
              <strong>Music prompt</strong>
              <p>{analysis?.music_prompt || 'A soundtrack direction will appear after prompt analysis.'}</p>
            </div>

            {analysisError && <div className="error-banner subtle">{analysisError}</div>}
          </div>

          {!isProcessing && !result && (
            <div className="glass-card info-panel">
              <p className="section-label">Studio tips</p>
              <h3>Premium prompts usually blend emotion, scene, light, and motion.</h3>
              <p className="page-copy">
                The cleanest outputs tend to come from one vivid sentence that names the atmosphere and the
                environment at the same time.
              </p>
              <div className="pill-row">
                <span className="dw-chip">Mood</span>
                <span className="dw-chip">Environment</span>
                <span className="dw-chip">Lighting</span>
                <span className="dw-chip">Movement</span>
              </div>
            </div>
          )}

          {isProcessing && <StepProgress progress={progress} currentStep={currentStep} />}

          {status === 'done' && savedEntry && (
            <div className="glass-card analysis-panel">
              <p className="section-label">Saved locally</p>
              <h2>Session added to your library</h2>
              <p className="page-copy">
                This result is stored in local browser history so it stays visible on the Library page even
                without journal endpoints on the backend.
              </p>
              <div className="pill-row">
                <span className="dw-chip">{savedEntry.art_style?.replace(/_/g, ' ') || 'Unknown style'}</span>
                <span className="dw-chip">{savedEntry.emotion || 'neutral'}</span>
              </div>
            </div>
          )}
        </aside>
      </div>

      {result && <ResultCard output={result} sourceText={submittedText} onNew={handleReset} />}
    </div>
  )
}
