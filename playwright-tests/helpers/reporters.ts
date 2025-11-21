/**
 * Custom Reporters für UAT-Artefakte
 * - Coverage-Matrix CSV
 * - Bug-List JSON
 * - HAR/Screenshot/Console-Aggregation
 */

import * as fs from 'fs';
import * as path from 'path';

export interface CoverageEntry {
  seite: string;
  rolle: string;
  create: 'OK' | 'FAIL' | 'N/A' | '';
  update: 'OK' | 'FAIL' | 'N/A' | '';
  delete: 'OK' | 'FAIL' | 'N/A' | '';
  workflow: 'OK' | 'FAIL' | 'N/A' | '';
  print: 'OK' | 'FAIL' | 'N/A' | '';
  export: 'OK' | 'FAIL' | 'N/A' | '';
  nav: 'OK' | 'FAIL' | 'N/A' | '';
  fallbackLevel: '1' | '2' | '3' | 'unknown' | '';
  ergebnis: 'PASS' | 'FAIL' | 'SKIP' | '';
  ticketID: string;
  runID: string;
  build: string;
}

export interface BugReport {
  id: string;
  seite: string;
  rolle: string;
  schritt: string;
  schweregrad: 'S1-Blocker' | 'S2-Hoch' | 'S3-Mittel' | 'S4-Niedrig';
  kurztitel: string;
  beschreibung: string;
  reproduktion: string[];
  umgebung: {
    browser: string;
    url: string;
    zeit: string;
    tenant: string;
    build: string;
  };
  artefakte: {
    screenshot?: string;
    har?: string;
    console?: string;
    server?: string;
  };
}

export class CoverageReporter {
  private entries: CoverageEntry[] = [];
  private outputPath: string;

  constructor(outputPath: string = 'docs/uat/COVERAGE-MATRIX.csv') {
    this.outputPath = outputPath;
  }

  addEntry(entry: CoverageEntry) {
    this.entries.push(entry);
  }

  generateCSV(): string {
    const headers = [
      'Seite',
      'Rolle',
      'Create',
      'Update',
      'Delete',
      'Workflow',
      'Print',
      'Export',
      'Nav',
      'FallbackLevel',
      'Ergebnis',
      'TicketID',
      'RunID',
      'Build',
    ];

    const rows = this.entries.map((entry) => [
      entry.seite,
      entry.rolle,
      entry.create,
      entry.update,
      entry.delete,
      entry.workflow,
      entry.print,
      entry.export,
      entry.nav,
      entry.fallbackLevel,
      entry.ergebnis,
      entry.ticketID,
      entry.runID,
      entry.build,
    ]);

    return [
      headers.join(','),
      ...rows.map((row) => row.join(',')),
    ].join('\n');
  }

  save() {
    const csv = this.generateCSV();
    const dir = path.dirname(this.outputPath);
    
    if (!fs.existsSync(dir)) {
      fs.mkdirSync(dir, { recursive: true });
    }

    fs.writeFileSync(this.outputPath, csv, 'utf-8');
    console.log(`Coverage-Matrix saved to: ${this.outputPath}`);
  }
}

export class BugReporter {
  private bugs: BugReport[] = [];
  private outputPath: string;
  private counter: number = 1;

  constructor(outputPath: string = 'docs/uat/BUGLIST.json') {
    this.outputPath = outputPath;
  }

  addBug(bug: Omit<BugReport, 'id'>): string {
    const id = `UAT-${String(this.counter).padStart(4, '0')}`;
    this.counter++;

    this.bugs.push({
      id,
      ...bug,
    });

    return id;
  }

  save() {
    const dir = path.dirname(this.outputPath);
    
    if (!fs.existsSync(dir)) {
      fs.mkdirSync(dir, { recursive: true });
    }

    fs.writeFileSync(this.outputPath, JSON.stringify(this.bugs, null, 2), 'utf-8');
    console.log(`Bug-List saved to: ${this.outputPath}`);
  }

  getBugs(): BugReport[] {
    return this.bugs;
  }

  getBugsBySeverity(severity: BugReport['schweregrad']): BugReport[] {
    return this.bugs.filter((bug) => bug.schweregrad === severity);
  }
}

export class ArtifactCollector {
  private artifactsDir: string;
  private runID: string;

  constructor(runID: string, baseDir: string = 'playwright-tests/artifacts') {
    this.runID = runID;
    this.artifactsDir = path.join(baseDir, runID);
    
    if (!fs.existsSync(this.artifactsDir)) {
      fs.mkdirSync(this.artifactsDir, { recursive: true });
    }
  }

  /**
   * Speichert Console-Logs
   */
  saveConsoleLogs(domain: string, spec: string, logs: string[]) {
    const dir = path.join(this.artifactsDir, domain);
    if (!fs.existsSync(dir)) {
      fs.mkdirSync(dir, { recursive: true });
    }

    const filename = path.join(dir, `${spec}-console.log`);
    fs.writeFileSync(filename, logs.join('\n'), 'utf-8');
  }

  /**
   * Sammelt Performance-Metriken
   */
  savePerformanceMetrics(domain: string, spec: string, metrics: any) {
    const dir = path.join(this.artifactsDir, domain);
    if (!fs.existsSync(dir)) {
      fs.mkdirSync(dir, { recursive: true });
    }

    const filename = path.join(dir, `${spec}-performance.json`);
    fs.writeFileSync(filename, JSON.stringify(metrics, null, 2), 'utf-8');
  }

  getArtifactsPath(): string {
    return this.artifactsDir;
  }
}

