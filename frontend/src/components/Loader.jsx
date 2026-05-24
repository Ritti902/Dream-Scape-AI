export default function Loader({ text = 'Loading', size = 42 }) {
  return (
    <div className="loader-shell" role="status" aria-live="polite">
      <span className="loader-ring" style={{ width: size, height: size }} />
      <span className="loader-text">{text}</span>
    </div>
  )
}
