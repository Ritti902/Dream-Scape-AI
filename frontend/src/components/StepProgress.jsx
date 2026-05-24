const STEPS = [
  'Reading your prompt',
  'Detecting emotion',
  'Developing the visual prompt',
  'Rendering the image',
  'Scoring and compositing',
  'Finalizing the export',
  'Dream ready',
]

function getActiveIndex(progress) {
  if (progress >= 100) return STEPS.length - 1
  if (progress >= 92) return 5
  if (progress >= 76) return 4
  if (progress >= 58) return 3
  if (progress >= 40) return 2
  if (progress >= 24) return 1
  return 0
}

export default function StepProgress({ progress = 0, currentStep = '' }) {
  const activeIndex = getActiveIndex(progress)

  return (
    <div className="progress-shell">
      <div className="progress-header">
        <div>
          <p className="section-label">Generation Progress</p>
          <h3>{currentStep || 'Preparing the pipeline'}</h3>
        </div>
        <div className="progress-figure">
          <strong>{progress}%</strong>
          <span>{progress >= 100 ? 'Complete' : 'Pipeline active'}</span>
        </div>
      </div>

      <div className="prog-track" aria-hidden="true">
        <div className="prog-fill" style={{ width: `${progress}%` }} />
      </div>

      <div className="step-list">
        {STEPS.map((step, index) => {
          const isDone = index < activeIndex
          const isActive = index === activeIndex
          const itemClass = isDone ? 'step-item done' : isActive ? 'step-item active' : 'step-item'

          return (
            <div key={step} className={itemClass}>
              <span className="step-marker">{isDone ? 'OK' : `${index + 1}`}</span>
              <div className="step-copy">
                <strong>{step}</strong>
                <span>{isDone ? 'Complete' : isActive ? 'In progress' : 'Queued'}</span>
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}
