/**
 * Fallback-Detector für 3-Ebenen-Fallback-System
 * Erkennt welche Ebene für Button-Aktionen greift:
 * - Level 1: Seitenspezifischer onClick
 * - Level 2: useListActions Hook
 * - Level 3: GlobalButtonHandler
 */

import { Page } from '@playwright/test';

export interface FallbackDetection {
  level: 1 | 2 | 3 | 'unknown';
  action: string;
  page: string;
  timestamp: string;
}

export class FallbackDetector {
  private consoleLogs: string[] = [];
  private page: Page;

  constructor(page: Page) {
    this.page = page;
    this.setupConsoleListener();
  }

  private setupConsoleListener() {
    this.page.on('console', (msg) => {
      const text = msg.text();
      this.consoleLogs.push(text);
    });
  }

  /**
   * Analysiert Console-Logs nach Fallback-Level-Meldungen
   */
  detectFallbackLevel(buttonAction: string): FallbackDetection {
    // Suche nach FB:LEVEL=X Meldungen in Console-Logs
    const fbPattern = /FB:LEVEL=(\d+)\s+PAGE=([^\s]+)\s+ACTION=([^\s]+)/;
    
    for (const log of this.consoleLogs.reverse()) {
      const match = log.match(fbPattern);
      if (match && match[3].toLowerCase().includes(buttonAction.toLowerCase())) {
        return {
          level: parseInt(match[1]) as 1 | 2 | 3,
          action: match[3],
          page: match[2],
          timestamp: new Date().toISOString(),
        };
      }
    }

    // Fallback: DOM-Inspektion
    return {
      level: 'unknown',
      action: buttonAction,
      page: this.page.url(),
      timestamp: new Date().toISOString(),
    };
  }

  /**
   * Prüft ob Button einen eigenen onClick-Handler hat (Level 1 Indikator)
   */
  async hasOwnClickHandler(buttonSelector: string): Promise<boolean> {
    return await this.page.evaluate((selector) => {
      const button = document.querySelector(selector) as HTMLButtonElement;
      if (!button) return false;
      
      // Prüfe ob onclick-Attribut oder Event-Listener existiert
      return button.onclick !== null || button.hasAttribute('onclick');
    }, buttonSelector);
  }

  /**
   * Extrahiert alle Fallback-Detections aus aktueller Session
   */
  getAllDetections(): FallbackDetection[] {
    const detections: FallbackDetection[] = [];
    const fbPattern = /FB:LEVEL=(\d+)\s+PAGE=([^\s]+)\s+ACTION=([^\s]+)/;

    for (const log of this.consoleLogs) {
      const match = log.match(fbPattern);
      if (match) {
        detections.push({
          level: parseInt(match[1]) as 1 | 2 | 3,
          action: match[3],
          page: match[2],
          timestamp: new Date().toISOString(),
        });
      }
    }

    return detections;
  }

  /**
   * Löscht Console-Logs (für neuen Test)
   */
  clearLogs() {
    this.consoleLogs = [];
  }
}

