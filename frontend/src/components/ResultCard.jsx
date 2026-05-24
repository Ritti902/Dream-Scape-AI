import { useState } from 'react'
import { getEmotionMeta, getThemeSummary, toPercent, updateDreamNote } from '../utils/helpers'

export default function ResultCard({ output, sourceText = '', onNew }) {
  const [note, setNote] = useState('')
  const [saved, setSaved] = useState(false)

  if (!output) return null

  const emotion = getEmotionMeta(output.emotion)
  const themeSummary = getThemeSummary(output.themes)
  const availableAssets = [
    output.video_url ? 'Video' : null,
    output.image_url ? 'Image' : null,
    output.music_url ? 'Soundtrack' : null,
  ].filter(Boolean)

  function handleSaveNote() {
    if (!note.trim()) return
    updateDreamNote(output.request_id, note.trim())
    setSaved(true)
    window.setTimeout(() => setSaved(false), 2000)
  }

  return (
    <section className="result-shell animate-fade-up">
      <div className="success-banner">
        <div className="success-copy">
          <p className="section-label">Dream generated</p>
          <strong>Render complete</strong>
          <span>Your prompt has been rendered into image, motion, and soundtrack output.</span>
        </div>
        <div className="success-actions">
          {availableAssets.map((asset) => (
            <span key={asset} className="dw-chip">
              {asset}
            </span>
          ))}
          <button className="btn-primary" type="button" onClick={onNew}>
            Create another dream
          </button>
        </div>
      </div>

      <div className="result-layout">
        <div className="stack-lg">
          <div className="glass-card media-panel">
            <div className="media-header">
              <div>
                <p className="section-label">Final Video</p>
                <h3>Cinematic export</h3>
              </div>
              {output.video_url && (
                <a className="btn-ghost" href={output.video_url} download>
                  Download video
                </a>
              )}
            </div>

            {output.video_url ? (
              <video className="media-frame" src={output.video_url} controls playsInline />
            ) : (
              <div className="empty-media">No video returned from the backend.</div>
            )}

            {output.music_url && (
              <div className="audio-frame">
                <p className="field-label">Soundtrack</p>
                <audio controls src={output.music_url} />
              </div>
            )}
          </div>

          <div className="glass-card media-panel">
            <div className="media-header">
              <div>
                <p className="section-label">Frame Render</p>
                <h3>Generated key art</h3>
              </div>
              {output.image_url && (
                <a className="btn-ghost" href={output.image_url} target="_blank" rel="noreferrer">
                  Open image
                </a>
              )}
            </div>

            {output.image_url ? (
              <img className="media-frame image-frame" src={output.image_url} alt="Generated dream scene" />
            ) : (
              <div className="empty-media">No image returned from the backend.</div>
            )}
          </div>
        </div>

        <div className="stack-lg">
          <div className="glass-card info-panel">
            <div className="section-block-header">
              <div>
                <p className="section-label">Emotion Profile</p>
                <h3>Output summary</h3>
              </div>
              <span className="tiny-note">{output.request_id || 'No request id'}</span>
            </div>

            <div className="emotion-hero">
              <span className="emotion-swatch" style={{ backgroundColor: emotion.color }} />
              <div>
                <h3>{emotion.label}</h3>
                <p>{emotion.description}</p>
              </div>
            </div>

            <div className="metric-row">
              <div>
                <span className="metric-title">Confidence</span>
                <strong>{toPercent(output.confidence)}</strong>
              </div>
              <div>
                <span className="metric-title">Art style</span>
                <strong>{output.art_style?.replace(/_/g, ' ') || 'Unknown'}</strong>
              </div>
            </div>

            <div className="metric-row">
              <div>
                <span className="metric-title">Seed</span>
                <strong>{output.seed}</strong>
              </div>
              <div>
                <span className="metric-title">Music source</span>
                <strong>{output.music_source || 'Unavailable'}</strong>
              </div>
            </div>

            <div className="pill-row">
              {(output.themes || []).map((theme) => (
                <span key={theme} className="dw-chip">
                  {theme}
                </span>
              ))}
            </div>
          </div>

          <div className="glass-card info-panel">
            <p className="section-label">Prompt Details</p>
            <div className="prompt-box">
              <strong>Original text</strong>
              <p>{sourceText || 'The original prompt was not stored.'}</p>
            </div>

            <div className="prompt-box">
              <strong>Theme summary</strong>
              <p>{themeSummary}</p>
            </div>

            <div className="prompt-box">
              <strong>Generated prompt</strong>
              <p>{output.prompt || 'No prompt text returned.'}</p>
            </div>
          </div>

          <div className="glass-card info-panel">
            <p className="section-label">Session Note</p>
            <textarea
              className="dw-textarea"
              rows={4}
              value={note}
              onChange={(event) => setNote(event.target.value)}
              placeholder="Capture what worked, what surprised you, or what prompt you want to try next."
            />
            <div className="inline-actions">
              <button className="btn-secondary" type="button" onClick={handleSaveNote}>
                {saved ? 'Note saved' : 'Save note locally'}
              </button>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
