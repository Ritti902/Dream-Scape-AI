import { useEffect, useRef, useState } from 'react'
import { startDream } from '../api/api'
import { saveDreamToHistory } from '../utils/helpers'

const PROGRESS_STEPS = [
  { progress: 10, label: 'Reading your prompt' },
  { progress: 24, label: 'Detecting emotion' },
  { progress: 40, label: 'Developing the visual prompt' },
  { progress: 58, label: 'Rendering the image' },
  { progress: 76, label: 'Scoring and compositing' },
  { progress: 92, label: 'Finalizing the export' },
]

export default function useDream() {
  const timerRef = useRef(null)
  const [status, setStatus] = useState('idle')
  const [progress, setProgress] = useState(0)
  const [currentStep, setCurrentStep] = useState('')
  const [result, setResult] = useState(null)
  const [savedEntry, setSavedEntry] = useState(null)
  const [error, setError] = useState('')

  useEffect(() => {
    return () => {
      if (timerRef.current) {
        clearInterval(timerRef.current)
      }
    }
  }, [])

  function clearTicker() {
    if (timerRef.current) {
      clearInterval(timerRef.current)
      timerRef.current = null
    }
  }

  function startTicker() {
    clearTicker()

    let stepIndex = 0
    setProgress(PROGRESS_STEPS[0].progress)
    setCurrentStep(PROGRESS_STEPS[0].label)

    timerRef.current = setInterval(() => {
      stepIndex = Math.min(stepIndex + 1, PROGRESS_STEPS.length - 1)
      setProgress(PROGRESS_STEPS[stepIndex].progress)
      setCurrentStep(PROGRESS_STEPS[stepIndex].label)
    }, 1400)
  }

  async function generate(payload) {
    clearTicker()
    setStatus('processing')
    setProgress(0)
    setCurrentStep('')
    setResult(null)
    setSavedEntry(null)
    setError('')
    startTicker()

    try {
      const response = await startDream(payload)
      clearTicker()
      setProgress(100)
      setCurrentStep('Dream ready')
      setResult(response)
      setSavedEntry(saveDreamToHistory(payload.text, response))
      setStatus('done')
    } catch (requestError) {
      clearTicker()
      setStatus('error')
      setError(requestError.message || 'Something went wrong while generating the dream.')
      setCurrentStep('')
      setProgress(0)
    }
  }

  function reset() {
    clearTicker()
    setStatus('idle')
    setProgress(0)
    setCurrentStep('')
    setResult(null)
    setSavedEntry(null)
    setError('')
  }

  return {
    currentStep,
    error,
    generate,
    progress,
    reset,
    result,
    savedEntry,
    status,
  }
}
