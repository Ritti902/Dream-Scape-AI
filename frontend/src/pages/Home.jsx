import { Link } from 'react-router-dom'

const FEATURE_CARDS = [
  {
    id: '01',
    title: 'Emotion analysis',
    description: 'The backend reads your text and classifies the dominant emotional signal.',
  },
  {
    id: '02',
    title: 'Prompt construction',
    description: 'Themes and mood cues are transformed into a single cinematic image prompt.',
  },
  {
    id: '03',
    title: 'Image and film render',
    description: 'A generated frame is animated into a short dream video with soundtrack output.',
  },
]

const STYLE_TAGS = [
  'Photorealistic',
  'Surrealist',
  'Anime',
  'Painterly',
  'Cyberpunk',
  'Watercolor',
  'Van Gogh',
]

const PROMPT_EXAMPLES = [
  'A lonely train platform under rain with the feeling of grief and distance.',
  'Weightless joy drifting above a neon city at sunrise.',
  'Stillness in an ancient garden lit by moonlight and cold mist.',
]

const HERO_METRICS = [
  {
    label: 'Live mood sensing',
    value: 'Emotion-aware',
    description: 'Prompt analysis responds while you type so the studio already feels guided before generation.',
  },
  {
    label: 'Local archive',
    value: 'Always saved',
    description: 'Sessions stay available in the browser with notes, art styles, timestamps, and media links.',
  },
  {
    label: 'Premium flow',
    value: 'One clean pass',
    description: 'Generation, review, and iteration now live inside a calmer workspace built like a high-end SaaS product.',
  },
]

export default function Home() {
  return (
    <div className="page">
      <section className="hero hero-home animate-fade-up">
        <div className="hero-copy glass-card">
          <div className="eyebrow-row">
            <p className="section-label">Premium Dream Studio</p>
            <span className="inline-badge">Minimal dark workspace</span>
          </div>
          <h1 className="hero-title">
            Turn raw emotion into a <span className="gradient-text">cinematic dream experience</span>.
          </h1>
          <p className="hero-text">
            Shape mood, lighting, style, and motion inside a cleaner interface designed to feel precise,
            calm, and premium from the first prompt to the final export.
          </p>

          <div className="hero-actions">
            <Link to="/generate" className="btn-primary">
              Open the studio
            </Link>
            <Link to="/history" className="btn-ghost">
              Browse the archive
            </Link>
          </div>

          <div className="hero-metrics">
            {HERO_METRICS.map((item) => (
              <article key={item.label} className="metric-panel">
                <span className="metric-title">{item.label}</span>
                <strong>{item.value}</strong>
                <p>{item.description}</p>
              </article>
            ))}
          </div>
        </div>

        <div className="hero-panel glass-card">
          <div className="panel-heading">
            <div>
              <p className="section-label">Studio preview</p>
              <h2>High-signal prompts that set the tone fast</h2>
            </div>
            <span className="inline-badge">Live analysis</span>
          </div>

          <div className="preview-list">
            {PROMPT_EXAMPLES.map((prompt, index) => (
              <article key={prompt} className="preview-card">
                <div className="preview-card-top">
                  <span className="preview-index">{`0${index + 1}`}</span>
                  <span className="preview-tag">{STYLE_TAGS[index]}</span>
                </div>
                <p>{prompt}</p>
              </article>
            ))}
          </div>

          <div className="workflow-preview">
            {FEATURE_CARDS.map((card) => (
              <div key={card.id} className="workflow-item">
                <span className="feature-index">{card.id}</span>
                <div>
                  <strong>{card.title}</strong>
                  <p>{card.description}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="content-section animate-fade-up delay-100">
        <div className="section-heading section-heading-split">
          <div>
            <p className="section-label">Design system</p>
            <h2>Structured surfaces, softer contrast, and better visual pacing</h2>
          </div>
          <p>
            Every major state now sits inside a clearer grid so prompts, controls, previews, and outputs feel
            more deliberate and easier to scan on both desktop and mobile.
          </p>
        </div>

        <div className="showcase-grid">
          <article className="glass-card feature-card feature-card-featured">
            <p className="section-label">Refined workflow</p>
            <h3>Built around the real backend flow without looking like an internal tool.</h3>
            <p>
              The app keeps the functional pieces that matter, then wraps them in calmer chrome, elevated
              spacing, and smoother interactions.
            </p>
            <div className="pill-row">
              {STYLE_TAGS.slice(0, 4).map((style) => (
                <span key={style} className="dw-chip">
                  {style}
                </span>
              ))}
            </div>
          </article>

          <div className="feature-stack">
            {FEATURE_CARDS.map((card) => (
              <article key={card.id} className="glass-card feature-card">
                <span className="feature-index">{card.id}</span>
                <h3>{card.title}</h3>
                <p>{card.description}</p>
              </article>
            ))}
          </div>
        </div>
      </section>

      <section className="content-section animate-fade-up delay-200">
        <div className="section-heading">
          <div>
            <p className="section-label">What improved</p>
            <h2>Cleaner visuals, stronger hierarchy, and fewer rough edges</h2>
          </div>
        </div>

        <div className="stats-grid">
          <article className="stat-card">
            <strong>Dark-first UI</strong>
            <span>Midnight surfaces, restrained gradients, and more breathable spacing across the full app.</span>
          </article>
          <article className="stat-card">
            <strong>Sharper studio flow</strong>
            <span>Prompting, settings, analysis, progress, and results now feel connected inside one workspace.</span>
          </article>
          <article className="stat-card">
            <strong>Polished library</strong>
            <span>Saved sessions are easier to browse, compare, and revisit with richer metadata and media cards.</span>
          </article>
        </div>
      </section>
    </div>
  )
}
