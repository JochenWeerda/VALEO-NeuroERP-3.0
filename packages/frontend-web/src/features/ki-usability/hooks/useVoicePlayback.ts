/**
 * Play synthesized voice (Piper audio) or browser SpeechSynthesis fallback.
 */

import { useCallback, useRef, useState } from 'react'
import { synthesizeVoice } from '../api/voice'

function base64ToBlob(base64: string, contentType: string): Blob {
  const binary = atob(base64)
  const bytes = new Uint8Array(binary.length)
  for (let i = 0; i < binary.length; i += 1) {
    bytes[i] = binary.charCodeAt(i)
  }
  return new Blob([bytes], { type: contentType })
}

function speakBrowser(text: string, language = 'de-DE'): boolean {
  if (!('speechSynthesis' in window)) return false
  window.speechSynthesis.cancel()
  const utterance = new SpeechSynthesisUtterance(text)
  utterance.lang = language
  window.speechSynthesis.speak(utterance)
  return true
}

export function useVoicePlayback() {
  const [playing, setPlaying] = useState(false)
  const audioRef = useRef<HTMLAudioElement | null>(null)
  const objectUrlRef = useRef<string | null>(null)

  const cleanup = useCallback(() => {
    if (audioRef.current) {
      audioRef.current.pause()
      audioRef.current = null
    }
    if (objectUrlRef.current) {
      URL.revokeObjectURL(objectUrlRef.current)
      objectUrlRef.current = null
    }
    setPlaying(false)
  }, [])

  const playText = useCallback(
    async (text: string, language = 'de-DE'): Promise<boolean> => {
      const trimmed = text.trim()
      if (!trimmed) return false

      cleanup()
      setPlaying(true)

      try {
        const result = await synthesizeVoice({ text: trimmed, language })
        if (result?.audio_base64 && result.content_type) {
          const blob = base64ToBlob(result.audio_base64, result.content_type)
          const url = URL.createObjectURL(blob)
          objectUrlRef.current = url
          const audio = new Audio(url)
          audioRef.current = audio
          await new Promise<void>((resolve, reject) => {
            audio.onended = () => resolve()
            audio.onerror = () => reject(new Error('Audio playback failed'))
            void audio.play().catch(reject)
          })
          return true
        }

        if (result?.browser_hint || !result?.audio_base64) {
          const ok = speakBrowser(trimmed, language)
          if (!ok) return false
          return true
        }

        return false
      } catch {
        return speakBrowser(trimmed, language)
      } finally {
        cleanup()
      }
    },
    [cleanup]
  )

  const stop = useCallback(() => {
    if ('speechSynthesis' in window) {
      window.speechSynthesis.cancel()
    }
    cleanup()
  }, [cleanup])

  return { playText, stop, playing }
}
