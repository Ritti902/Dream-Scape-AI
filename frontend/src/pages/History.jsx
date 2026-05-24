import { Link } from 'react-router-dom'
import {
  formatDate,
  getDominantEmotion,
  getDreamHistory,
  getEmotionMeta,
  getThemeSummary,
  toPercent,
  truncate,
} from '../utils/helpers'

function HistoryEntry({ entry }) {
  const emotion = getEmotionMeta(entry.emotion)

  return (
    <article className="glass-card history-card">
      <div className="history-media">
        {entry.image_url ? (
          <img src={entry.image_url} alt="Generated dream artwork" />
        ) : (
          <div className="empty-media compact">No image</div>
        )}
      </div>

      <div className="history-body">
        <div className="history-top">
          <div className="history-heading">
            <span className="emotion-pill" style={{ borderColor: `${emotion.color}55`, color: emotion.color }}>
              {emotion.label}
            </span>
            <strong>{entry.art_style?.replace(/_/g, ' ') || 'Unknown style'}</strong>
          </div>
          <span className="tiny-note">{formatDate(entry.created_at)}</span>
        </div>

        <p className="history-text">{truncate(entry.text, 170)}</p>

        <div className="history-meta-grid">
          <div className="metric-panel compact">
            <span className="metric-title">Confidence</span>
            <strong>{toPercent(entry.confidence)}</strong>
          </div>
          <div className="metric-panel compact">
            <span className="metric-title">Seed</span>
            <strong>{entry.seed ?? 'Random'}</strong>
          </div>
        </div>

        <div className="prompt-box compact">
          <strong>Themes</strong>
          <p>{getThemeSummary(entry.themes)}</p>
        </div>

        {entry.note && (
          <div className="prompt-box compact">
            <strong>Note</strong>
            <p>{entry.note}</p>
          </div>
        )}

        <div className="history-actions">
          {entry.video_url && (
            <a className="btn-primary" href={entry.video_url} target="_blank" rel="noreferrer">
              Open video
            </a>
          )}
          {entry.music_url && (
            <a className="btn-ghost" href={entry.music_url} target="_blank" rel="noreferrer">
              Open audio
            </a>
          )}
        </div>
      </div>
    </article>
  )
}

export default function History() {
  const entries = getDreamHistory()
  const dominantEmotion = getEmotionMeta(getDominantEmotion(entries))
  const latestStyle = entries[0]?.art_style?.replace(/_/g, ' ') || 'None yet'

  return (
    <div className="page">
      <section className="glass-card archive-hero animate-fade-up">
        <div className="archive-hero-copy">
          <div className="eyebrow-row">
            <p className="section-label">Library</p>
            <span className="inline-badge">Browser-saved sessions</span>
          </div>
          <h1 className="page-title">Your local dream archive</h1>
          <p className="page-copy">
            Browse previous generations, reopen media, and keep lightweight notes without waiting on backend
            journal endpoints.
          </p>
          <div className="pill-row">
            <span className="dw-chip">Reusable prompts</span>
            <span className="dw-chip">Saved notes</span>
            <span className="dw-chip">Fast media access</span>
          </div>
        </div>

        <div className="archive-overview">
          <article className="stat-card">
            <strong>{entries.length}</strong>
            <span>Saved sessions</span>
          </article>
          <article className="stat-card">
            <strong>{dominantEmotion.label}</strong>
            <span>Most common emotion</span>
          </article>
          <article className="stat-card">
            <strong>{latestStyle}</strong>
            <span>Latest art style</span>
          </article>
        </div>
      </section>

      {entries.length === 0 ? (
        <section className="glass-card empty-state animate-fade-up delay-200">
          <p className="section-label">No sessions yet</p>
          <h2>The library fills up after your first successful generation.</h2>
          <p>
            Create a dream in the studio and it will be stored here automatically with its media links and notes.
          </p>
          <Link to="/generate" className="btn-primary">
            Go to the studio
          </Link>
        </section>
      ) : (
        <section className="history-list animate-fade-up delay-200">
          {entries.map((entry) => (
            <HistoryEntry key={entry.request_id} entry={entry} />
          ))}
        </section>
      )}
    </div>
  )
}
