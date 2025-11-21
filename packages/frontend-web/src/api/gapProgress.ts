/**
 * GAP Pipeline Progress API Client
 */

import { apiClient } from '../lib/api-client'

export interface PipelineStep {
  completed: boolean
  name: string
}

export interface PipelineProgress {
  job_id: string
  year: number
  current_step: string
  progress: number
  total_steps: number
  percentage: number
  message: string
  status: 'running' | 'completed' | 'error'
  updated_at: string
  steps: Record<string, PipelineStep>
}

/**
 * Holt den aktuellen Fortschritt einer Pipeline-Ausführung
 */
export async function getPipelineProgress(jobId: string): Promise<PipelineProgress> {
  const response = await apiClient.get(`/api/v1/gap/pipeline/progress/${jobId}`)
  return response.data
}

/**
 * Überwacht Pipeline-Progress mit Polling
 */
export class PipelineProgressMonitor {
  private jobId: string
  private intervalId: number | null = null
  private onUpdate: (progress: PipelineProgress) => void
  private onComplete: (progress: PipelineProgress) => void
  private onError: (error: string) => void

  constructor(
    jobId: string,
    callbacks: {
      onUpdate: (progress: PipelineProgress) => void
      onComplete: (progress: PipelineProgress) => void
      onError: (error: string) => void
    }
  ) {
    this.jobId = jobId
    this.onUpdate = callbacks.onUpdate
    this.onComplete = callbacks.onComplete
    this.onError = callbacks.onError
  }

  start(intervalMs: number = 2000): void {
    this.stop() // Stop existing polling

    const poll = async () => {
      try {
        const progress = await getPipelineProgress(this.jobId)
        this.onUpdate(progress)

        if (progress.status === 'completed') {
          this.onComplete(progress)
          this.stop()
        } else if (progress.status === 'error') {
          this.onError(progress.message)
          this.stop()
        }
      } catch (error: any) {
        if (error.response?.status === 404) {
          // Job nicht gefunden - möglicherweise noch nicht gestartet oder abgelaufen
          return
        }
        this.onError(error.message || 'Fehler beim Abrufen des Pipeline-Status')
        this.stop()
      }
    }

    // Erste Abfrage sofort
    poll()

    // Dann regelmäßig pollen
    this.intervalId = window.setInterval(poll, intervalMs)
  }

  stop(): void {
    if (this.intervalId) {
      clearInterval(this.intervalId)
      this.intervalId = null
    }
  }
}
