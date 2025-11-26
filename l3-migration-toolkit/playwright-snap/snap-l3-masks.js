/**
 * L3-Masken Screenshot-Automatisierung
 * 
 * Navigiert durch die wichtigsten L3-Masken und erstellt Screenshots
 * für die Dokumentation und Analyse der Migration zu VALEO-NeuroERP.
 */

const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

// Konfiguration
const CONFIG = {
  guacamoleUrl: 'http://localhost:8090/guacamole/#/client/MQBjAHBvc3RncmVzcWw',
  outputDir: path.join(__dirname, '../screenshots/l3-masks'),
  delay: 2000, // Wartezeit zwischen Aktionen (ms)
  clickDelay: 500, // Wartezeit nach Klick (ms)
};

// L3-Masken-Inventar mit Navigations-Koordinaten
const L3_MASKS = [
  {
    id: 'artikel-stamm',
    name: 'Artikel-Stamm',
    menu: 'FAVORITEN',
    menuCoords: { x: 400, y: 100 }, // Ungefähre Position im Top-Menü
    description: 'Artikelverwaltung - Hauptmaske für Artikelstammdaten'
  },
  {
    id: 'kunden-artikel',
    name: 'Kunden-Artikel',
    menu: 'FAVORITEN',
    menuCoords: { x: 300, y: 100 },
    description: 'Kundenbezogene Artikelverwaltung'
  },
  {
    id: 'verkauf-lieferschein',
    name: 'Verkauf-Lieferschein',
    menu: 'FAVORITEN',
    menuCoords: { x: 500, y: 100 },
    description: 'Lieferschein-Erfassung'
  },
  {
    id: 'erfassung-auftrag',
    name: 'Auftrag erfassen',
    menu: 'ERFASSUNG',
    menuCoords: { x: 0, y: 0 }, // TODO: Koordinaten ermitteln
    description: 'Auftragserfassung'
  },
  {
    id: 'abrechnung-rechnung',
    name: 'Rechnung',
    menu: 'ABRECHNUNG',
    menuCoords: { x: 0, y: 0 },
    description: 'Rechnungserstellung'
  },
  {
    id: 'lager-bestand',
    name: 'Lager-Bestand',
    menu: 'LAGER',
    menuCoords: { x: 0, y: 0 },
    description: 'Lagerverwaltung'
  },
];

/**
 * Erstellt Screenshot-Verzeichnis
 */
function ensureOutputDir() {
  if (!fs.existsSync(CONFIG.outputDir)) {
    fs.mkdirSync(CONFIG.outputDir, { recursive: true });
    console.log(`✅ Screenshot-Verzeichnis erstellt: ${CONFIG.outputDir}`);
  }
}

/**
 * Wartet für eine bestimmte Zeit
 */
function wait(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

/**
 * Erstellt Screenshot einer L3-Maske
 */
async function captureMask(page, mask, index) {
  console.log(`\n📸 [${index + 1}/${L3_MASKS.length}] Erfasse: ${mask.name}`);
  
  try {
    // Wenn Koordinaten definiert sind, klicke auf das Menü
    if (mask.menuCoords.x > 0 && mask.menuCoords.y > 0) {
      console.log(`   ↪ Navigiere über Menü: ${mask.menu}`);
      
      // Klicke auf Canvas (RDP-Oberfläche)
      const canvas = await page.locator('canvas').first();
      await canvas.click({
        position: mask.menuCoords,
        timeout: 5000
      });
      
      await wait(CONFIG.clickDelay);
    }
    
    // Warte auf Maskendarstellung
    await wait(CONFIG.delay);
    
    // Screenshot erstellen
    const filename = `${String(index + 1).padStart(2, '0')}_${mask.id}.png`;
    const filepath = path.join(CONFIG.outputDir, filename);
    
    await page.screenshot({
      path: filepath,
      fullPage: false,
    });
    
    console.log(`   ✅ Gespeichert: ${filename}`);
    
    // Metadaten speichern
    return {
      id: mask.id,
      name: mask.name,
      description: mask.description,
      filename: filename,
      timestamp: new Date().toISOString(),
    };
    
  } catch (error) {
    console.error(`   ❌ Fehler bei ${mask.name}:`, error.message);
    return null;
  }
}

/**
 * Haupt-Funktion: Erfasst alle L3-Masken
 */
async function captureAllMasks() {
  console.log('🚀 L3-Masken Screenshot-Automatisierung gestartet\n');
  
  ensureOutputDir();
  
  const browser = await chromium.launch({
    headless: false, // Browser sichtbar für Debugging
    slowMo: 100, // Verlangsamung für bessere Sichtbarkeit
  });
  
  const context = await browser.newContext({
    viewport: { width: 1920, height: 1080 },
  });
  
  const page = await context.newPage();
  
  try {
    // Navigiere zu Guacamole RDP-Verbindung
    console.log('🔗 Verbinde zu Guacamole...');
    await page.goto(CONFIG.guacamoleUrl, { waitUntil: 'networkidle' });
    await wait(3000); // Warte auf RDP-Verbindung
    
    // Initialer Screenshot (Startseite/Kalender)
    console.log('\n📸 [0] Erfasse: L3-Startseite (Kalender)');
    await page.screenshot({
      path: path.join(CONFIG.outputDir, '00_l3-startseite.png'),
    });
    console.log('   ✅ Gespeichert: 00_l3-startseite.png');
    
    // Erfasse alle Masken
    const results = [];
    for (let i = 0; i < L3_MASKS.length; i++) {
      const mask = L3_MASKS[i];
      const result = await captureMask(page, mask, i);
      if (result) {
        results.push(result);
      }
      
      // Pause zwischen Masken
      await wait(500);
    }
    
    // Speichere Metadaten-Index
    const indexPath = path.join(CONFIG.outputDir, 'index.json');
    fs.writeFileSync(
      indexPath,
      JSON.stringify({
        generatedAt: new Date().toISOString(),
        totalMasks: results.length,
        masks: results,
      }, null, 2)
    );
    
    console.log(`\n✅ Screenshot-Index gespeichert: index.json`);
    console.log(`\n🎉 Erfolgreich ${results.length} Masken dokumentiert!`);
    
  } catch (error) {
    console.error('\n❌ Fehler:', error);
  } finally {
    console.log('\n🔒 Browser schließen...');
    await browser.close();
  }
}

/**
 * Manuelle Screenshot-Funktion (für interaktive Nutzung)
 */
async function manualScreenshot(maskId) {
  const mask = L3_MASKS.find(m => m.id === maskId);
  if (!mask) {
    console.error(`❌ Maske nicht gefunden: ${maskId}`);
    return;
  }
  
  ensureOutputDir();
  
  const browser = await chromium.launch({ headless: false });
  const page = await browser.newPage();
  
  await page.goto(CONFIG.guacamoleUrl);
  await wait(3000);
  
  await captureMask(page, mask, 0);
  
  await browser.close();
}

// CLI-Ausführung
if (require.main === module) {
  const args = process.argv.slice(2);
  
  if (args.length > 0 && args[0] === '--manual') {
    // Manueller Modus: node snap-l3-masks.js --manual artikel-stamm
    const maskId = args[1];
    if (!maskId) {
      console.error('❌ Bitte Masken-ID angeben: --manual <maskId>');
      process.exit(1);
    }
    manualScreenshot(maskId);
  } else {
    // Automatischer Modus: Alle Masken
    captureAllMasks();
  }
}

module.exports = { captureAllMasks, manualScreenshot, L3_MASKS };

