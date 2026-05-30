/**
 * Record microphone audio via MediaRecorder for local faster-whisper STT.
 */

export type LocalVoiceCaptureResult = {
  audioBase64: string
  audioFormat: 'webm' | 'ogg' | 'wav'
}

const DEFAULT_MAX_MS = 15_000

function pickMimeType(): { mimeType: string; format: LocalVoiceCaptureResult['audioFormat'] } {
  if (typeof MediaRecorder !== 'undefined' && MediaRecorder.isTypeSupported('audio/webm;codecs=opus')) {
    return { mimeType: 'audio/webm;codecs=opus', format: 'webm' }
  }
  if (typeof MediaRecorder !== 'undefined' && MediaRecorder.isTypeSupported('audio/ogg;codecs=opus')) {
    return { mimeType: 'audio/ogg;codecs=opus', format: 'ogg' }
  }
  return { mimeType: 'audio/webm', format: 'webm' }
}

function blobToBase64(blob: Blob): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.onloadend = () => {
      const dataUrl = reader.result
      if (typeof dataUrl !== 'string') {
        reject(new Error('FileReader returned no data URL'))
        return
      }
      const comma = dataUrl.indexOf(',')
      resolve(comma >= 0 ? dataUrl.slice(comma + 1) : dataUrl)
    }
    reader.onerror = () => reject(reader.error ?? new Error('FileReader failed'))
    reader.readAsDataURL(blob)
  })
}

export async function captureLocalVoiceAudio(maxMs = DEFAULT_MAX_MS): Promise<LocalVoiceCaptureResult> {
  if (!navigator.mediaDevices?.getUserMedia) {
    throw new Error('Mikrofon-API nicht verfügbar')
  }
  if (typeof MediaRecorder === 'undefined') {
    throw new Error('MediaRecorder nicht verfügbar')
  }

  const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
  const { mimeType, format } = pickMimeType()
  const recorder = new MediaRecorder(stream, { mimeType })
  const chunks: Blob[] = []

  return new Promise((resolve, reject) => {
    const timeout = window.setTimeout(() => {
      if (recorder.state === 'recording') recorder.stop()
    }, maxMs)

    recorder.ondataavailable = (event) => {
      if (event.data.size > 0) chunks.push(event.data)
    }

    recorder.onerror = () => {
      window.clearTimeout(timeout)
      stream.getTracks().forEach((track) => track.stop())
      reject(new Error('Audio-Aufnahme fehlgeschlagen'))
    }

    recorder.onstop = async () => {
      window.clearTimeout(timeout)
      stream.getTracks().forEach((track) => track.stop())
      try {
        const blob = new Blob(chunks, { type: mimeType })
        if (!blob.size) {
          reject(new Error('Keine Audiodaten aufgenommen'))
          return
        }
        const audioBase64 = await blobToBase64(blob)
        resolve({ audioBase64, audioFormat: format })
      } catch (err) {
        reject(err)
      }
    }

    recorder.start()
  })
}

export function isLocalVoiceCaptureSupported(): boolean {
  return Boolean(
    typeof window !== 'undefined'
    && typeof navigator?.mediaDevices?.getUserMedia === 'function'
    && typeof MediaRecorder !== 'undefined',
  )
}

export function resolveVoiceSttProvider(): 'local' | 'browser' {
  const env = (import.meta.env as Record<string, string | undefined>).VITE_VOICE_STT_PROVIDER?.trim().toLowerCase()
  if (env === 'browser') return 'browser'
  if (env === 'local') return 'local'
  return isLocalVoiceCaptureSupported() ? 'local' : 'browser'
}
