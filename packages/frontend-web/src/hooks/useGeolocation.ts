/**
 * Geolocation Hook
 *
 * GPS-Integration für Field Service Anwendungen:
 * - Aktuelle Position
 * - Position-Tracking (Continuous)
 * - Distanz- und Fahrzeitberechnung
 * - Offline-Queue mit Position
 */

import { useState, useEffect, useCallback, useRef } from 'react'

export interface GeoPosition {
  latitude: number
  longitude: number
  accuracy: number
  altitude?: number | null
  altitudeAccuracy?: number | null
  heading?: number | null
  speed?: number | null
  timestamp: number
}

export interface GeoError {
  code: number
  message: string
}

interface UseGeolocationOptions {
  /** Hohe Genauigkeit (GPS) - verbraucht mehr Batterie */
  enableHighAccuracy?: boolean
  /** Maximale Zeit für Position (ms) */
  timeout?: number
  /** Maximales Alter der gecachten Position (ms) */
  maximumAge?: number
  /** Kontinuierliches Tracking */
  continuous?: boolean
  /** Callback bei neuer Position */
  onPosition?: (position: GeoPosition) => void
  /** Callback bei Fehler */
  onError?: (error: GeoError) => void
}

interface UseGeolocationReturn {
  /** Aktuelle Position */
  position: GeoPosition | null
  /** Letzte Fehler */
  error: GeoError | null
  /** Wird geladen */
  loading: boolean
  /** Geolocation unterstützt */
  supported: boolean
  /** Tracking aktiv */
  isTracking: boolean
  /** Position einmalig abrufen */
  getCurrentPosition: () => Promise<GeoPosition>
  /** Tracking starten */
  startTracking: () => void
  /** Tracking stoppen */
  stopTracking: () => void
  /** Position-Historie */
  history: GeoPosition[]
  /** Historie leeren */
  clearHistory: () => void
}

/**
 * Hook für Geolocation API
 */
export function useGeolocation(options: UseGeolocationOptions = {}): UseGeolocationReturn {
  const {
    enableHighAccuracy = true,
    timeout = 10000,
    maximumAge = 0,
    continuous = false,
    onPosition,
    onError,
  } = options

  const [position, setPosition] = useState<GeoPosition | null>(null)
  const [error, setError] = useState<GeoError | null>(null)
  const [loading, setLoading] = useState(false)
  const [isTracking, setIsTracking] = useState(false)
  const [history, setHistory] = useState<GeoPosition[]>([])
  const watchIdRef = useRef<number | null>(null)

  const supported = typeof navigator !== 'undefined' && 'geolocation' in navigator

  // Position aus GeolocationPosition extrahieren
  const extractPosition = useCallback((geoPos: GeolocationPosition): GeoPosition => {
    return {
      latitude: geoPos.coords.latitude,
      longitude: geoPos.coords.longitude,
      accuracy: geoPos.coords.accuracy,
      altitude: geoPos.coords.altitude,
      altitudeAccuracy: geoPos.coords.altitudeAccuracy,
      heading: geoPos.coords.heading,
      speed: geoPos.coords.speed,
      timestamp: geoPos.timestamp,
    }
  }, [])

  // Fehler-Handler
  const handleError = useCallback((geoError: GeolocationPositionError) => {
    const err: GeoError = {
      code: geoError.code,
      message: geoError.message,
    }
    setError(err)
    onError?.(err)
  }, [onError])

  // Position-Handler
  const handlePosition = useCallback((geoPos: GeolocationPosition) => {
    const pos = extractPosition(geoPos)
    setPosition(pos)
    setError(null)
    setLoading(false)

    // Zur Historie hinzufügen
    setHistory(prev => [...prev.slice(-99), pos]) // Max 100 Einträge

    onPosition?.(pos)
  }, [extractPosition, onPosition])

  // Einmalige Position abrufen
  const getCurrentPosition = useCallback((): Promise<GeoPosition> => {
    return new Promise((resolve, reject) => {
      if (!supported) {
        reject(new Error('Geolocation nicht unterstützt'))
        return
      }

      setLoading(true)
      setError(null)

      navigator.geolocation.getCurrentPosition(
        (geoPos) => {
          const pos = extractPosition(geoPos)
          setPosition(pos)
          setLoading(false)
          onPosition?.(pos)
          resolve(pos)
        },
        (geoError) => {
          handleError(geoError)
          setLoading(false)
          reject(geoError)
        },
        {
          enableHighAccuracy,
          timeout,
          maximumAge,
        }
      )
    })
  }, [supported, enableHighAccuracy, timeout, maximumAge, extractPosition, handleError, onPosition])

  // Tracking starten
  const startTracking = useCallback(() => {
    if (!supported || isTracking) return

    setIsTracking(true)
    setLoading(true)

    watchIdRef.current = navigator.geolocation.watchPosition(
      handlePosition,
      handleError,
      {
        enableHighAccuracy,
        timeout,
        maximumAge,
      }
    )
  }, [supported, isTracking, enableHighAccuracy, timeout, maximumAge, handlePosition, handleError])

  // Tracking stoppen
  const stopTracking = useCallback(() => {
    if (watchIdRef.current !== null) {
      navigator.geolocation.clearWatch(watchIdRef.current)
      watchIdRef.current = null
    }
    setIsTracking(false)
  }, [])

  // Historie leeren
  const clearHistory = useCallback(() => {
    setHistory([])
  }, [])

  // Continuous Tracking
  useEffect(() => {
    if (continuous && supported) {
      startTracking()
    }

    return () => {
      stopTracking()
    }
  }, [continuous, supported, startTracking, stopTracking])

  // Cleanup
  useEffect(() => {
    return () => {
      if (watchIdRef.current !== null) {
        navigator.geolocation.clearWatch(watchIdRef.current)
      }
    }
  }, [])

  return {
    position,
    error,
    loading,
    supported,
    isTracking,
    getCurrentPosition,
    startTracking,
    stopTracking,
    history,
    clearHistory,
  }
}

/**
 * Berechnet Distanz zwischen zwei Punkten (Haversine-Formel)
 * @returns Distanz in Metern
 */
export function calculateDistance(
  lat1: number,
  lon1: number,
  lat2: number,
  lon2: number
): number {
  const R = 6371000 // Erdradius in Metern
  const dLat = toRadians(lat2 - lat1)
  const dLon = toRadians(lon2 - lon1)

  const a =
    Math.sin(dLat / 2) * Math.sin(dLat / 2) +
    Math.cos(toRadians(lat1)) * Math.cos(toRadians(lat2)) *
    Math.sin(dLon / 2) * Math.sin(dLon / 2)

  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a))

  return R * c
}

function toRadians(degrees: number): number {
  return degrees * (Math.PI / 180)
}

/**
 * Formatiert Distanz für Anzeige
 */
export function formatDistance(meters: number): string {
  if (meters < 1000) {
    return `${Math.round(meters)} m`
  }
  return `${(meters / 1000).toFixed(1)} km`
}

/**
 * Berechnet geschätzte Fahrzeit
 * @param meters Distanz in Metern
 * @param speedKmh Durchschnittsgeschwindigkeit in km/h (Standard: 50)
 * @returns Fahrzeit in Minuten
 */
export function estimateTravelTime(meters: number, speedKmh = 50): number {
  const km = meters / 1000
  const hours = km / speedKmh
  return Math.round(hours * 60)
}

/**
 * Formatiert Fahrzeit für Anzeige
 */
export function formatTravelTime(minutes: number): string {
  if (minutes < 60) {
    return `${minutes} Min.`
  }
  const hours = Math.floor(minutes / 60)
  const mins = minutes % 60
  return `${hours} Std. ${mins} Min.`
}

/**
 * Generiert Google Maps Navigationslink
 */
export function getNavigationUrl(
  destLat: number,
  destLon: number,
  mode: 'driving' | 'walking' | 'transit' = 'driving'
): string {
  return `https://www.google.com/maps/dir/?api=1&destination=${destLat},${destLon}&travelmode=${mode}`
}

/**
 * Generiert Apple Maps Navigationslink
 */
export function getAppleMapsUrl(destLat: number, destLon: number): string {
  return `https://maps.apple.com/?daddr=${destLat},${destLon}&dirflg=d`
}

/**
 * Erkennt ob iOS Gerät
 */
export function isIOS(): boolean {
  return /iPad|iPhone|iPod/.test(navigator.userAgent)
}

/**
 * Öffnet Navigation in passender App
 */
export function openNavigation(destLat: number, destLon: number): void {
  const url = isIOS()
    ? getAppleMapsUrl(destLat, destLon)
    : getNavigationUrl(destLat, destLon)

  window.open(url, '_blank')
}
