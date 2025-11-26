/**
 * FINALE L3 Auto-Navigator (Playwright)
 * 
 * Nutzt page.mouse.click() für ECHTE Maus-Events in Guacamole RDP.
 * Prozentuale Koordinaten aus CSV, Canvas-BoundingBox-basiert.
 * 
 * VOLLAUTOMATISCH - NO HANDS ON!
 */

const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');
const csv = require('csv-parse/sync');

// Konfiguration
const CONFIG = {
  guacamoleUrl: 'http://localhost:8090/guacamole/#/client/MQBjAHBvc3RncmVzcWw',
  csvPath: path.join(__dirname, 'l3_gui_map.csv'),
  outputDir: path.join(__dirname, 'screenshots/l3-masks-auto'),
  originalCanvasSize: { width: 1920, height: 1024 }, // Referenz-Größe aus CSV
  calibration: { dx: 0, dy: 0 }, // Kalibrierungs-Offset (falls nötig)
};

// GUI-Map laden
function loadGuiMap(csvPath) {
  const csvContent = fs.readFileSync(csvPath, 'utf-8');
  const records = csv.parse(csvContent, {
    columns: true,
    skip_empty_lines: true
  });
  
  const guiMap = { tabs: {}, ribbon: {} };
  
  records.forEach(row => {
    const elem = {
      x_pct: parseFloat(row.x_pct),
      y_pct: parseFloat(row.y_pct),
      submenu_y_pct: row.submenu_y_pct ? parseFloat(row.submenu_y_pct) : null
    };
    
    if (row.group === 'tabs') guiMap.tabs[row.name] = elem;
    else if (row.group === 'ribbon') guiMap.ribbon[row.name] = elem;
  });
  
  return guiMap;
}

// ROBUSTE Klick-Funktion (page.mouse mit Canvas-BoundingBox)
async function clickGuacPct(page, xPct, yPct, elementName = 'Element') {
  // Canvas BoundingBox holen
  const box = await page.locator('canvas').first().boundingBox();
  
  if (!box) {
    console.error('❌ Canvas boundingBox nicht gefunden');
    return false;
  }
  
  // Original-Koordinaten (basierend auf 1920x1024)
  const originalX = CONFIG.originalCanvasSize.width * (xPct / 100);
  const originalY = CONFIG.originalCanvasSize.height * (yPct / 100);
  
  // Skalierung
  const scaleX = box.width / CONFIG.originalCanvasSize.width;
  const scaleY = box.height / CONFIG.originalCanvasSize.height;
  
  // Absolute Koordinaten (skaliert + Canvas-Offset + Kalibrierung)
  const x = Math.round(box.x + originalX * scaleX + CONFIG.calibration.dx);
  const y = Math.round(box.y + originalY * scaleY + CONFIG.calibration.dy);
  
  console.log(`   🖱️  Klicke '${elementName}' bei (${x}, ${y}) = (${xPct}%, ${yPct}%)`);
  console.log(`       Canvas: ${box.width}x${box.height}, Skalierung: ${(scaleX * 100).toFixed(1)}%`);
  
  // Fokussiere Canvas ZUERST (wichtig!)
  await page.locator('canvas').first().click({ position: { x: 5, y: 5 } });
  await page.waitForTimeout(100);
  
  // ECHTER Maus-Klick (nicht DOM-Event!)
  await page.mouse.move(x, y);
  await page.mouse.down({ button: 'left' });
  await page.waitForTimeout(50);
  await page.mouse.up({ button: 'left' });
  
  return true;
}

// Screenshot erstellen
async function captureScreenshot(page, maskId, outputDir) {
  const filename = `${maskId}.png`;
  const filepath = path.join(outputDir, filename);
  
  await page.screenshot({ path: filepath, fullPage: false });
  
  console.log(`   ✅ Screenshot: ${filename}`);
  return filepath;
}

// L3-Masken Definitionen
const L3_MASKS = [
  { id: 'kundenstamm', name: 'Kundenstamm', nav: [{ type: 'ribbon', elem: 'Kunden', wait: 3000 }] },
  { id: 'lieferanten', name: 'Lieferantenstamm', nav: [{ type: 'ribbon', elem: 'Lieferanten', wait: 3000 }] },
  { id: 'crm', name: 'CRM Dashboard', nav: [{ type: 'ribbon', elem: 'CRM', wait: 3000 }] },
  { id: 'kalender', name: 'Kalender', nav: [{ type: 'ribbon', elem: 'Kalender', wait: 2000 }] },
  { id: 'angebot_auftrag', name: 'Angebot/Auftrag', nav: [{ type: 'ribbon', elem: 'Angebot_Auftrag', wait: 3000 }] },
  { id: 'einkauf', name: 'Einkauf-Verwaltung', nav: [{ type: 'ribbon', elem: 'Einkauf_Waren', wait: 3000 }] },
  { id: 'erfassung_tab', name: 'ERFASSUNG Tab', nav: [{ type: 'tab', elem: 'ERFASSUNG', wait: 1000 }] },
  { id: 'abrechnung_tab', name: 'ABRECHNUNG Tab', nav: [{ type: 'tab', elem: 'ABRECHNUNG', wait: 1000 }] },
  { id: 'lager_tab', name: 'LAGER Tab', nav: [{ type: 'tab', elem: 'LAGER', wait: 1000 }] },
];

// Navigiere zu Maske
async function navigateToMask(page, guiMap, maskConfig) {
  console.log(`\n🧭 Navigiere zu: ${maskConfig.name}`);
  
  for (const step of maskConfig.nav) {
    const elemMap = step.type === 'tab' ? guiMap.tabs : guiMap.ribbon;
    const elem = elemMap[step.elem];
    
    if (!elem) {
      console.error(`   ❌ Element '${step.elem}' nicht gefunden`);
      return false;
    }
    
    const success = await clickGuacPct(page, elem.x_pct, elem.y_pct, step.elem);
    if (!success) return false;
    
    await page.waitForTimeout(step.wait);
    
    // Submenu (falls vorhanden)
    if (elem.submenu_y_pct) {
      console.log(`   🖱️  Klicke Submenu bei ${elem.submenu_y_pct}%`);
      await clickGuacPct(page, elem.x_pct, elem.submenu_y_pct, `${step.elem} Submenu`);
      await page.waitForTimeout(1000);
    }
  }
  
  return true;
}

// Hauptfunktion
async function captureAllMasks() {
  console.log('🚀 L3 Vollautomatische Masken-Erfassung (page.mouse)\n');
  
  // Output-Verzeichnis
  if (!fs.existsSync(CONFIG.outputDir)) {
    fs.mkdirSync(CONFIG.outputDir, { recursive: true });
  }
  
  // GUI-Map laden
  const guiMap = loadGuiMap(CONFIG.csvPath);
  console.log(`✅ GUI-Map: ${Object.keys(guiMap.tabs).length} Tabs, ${Object.keys(guiMap.ribbon).length} Ribbon\n`);
  
  // Browser starten
  const browser = await chromium.launch({ headless: false });
  const context = await browser.newContext({ viewport: null }); // Keine feste Viewport-Größe
  const page = await context.newPage();
  
  try {
    // Navigiere zu Guacamole
    console.log('🔗 Verbinde zu Guacamole...');
    await page.goto(CONFIG.guacamoleUrl);
    await page.waitForTimeout(3000); // RDP-Verbindung laden
    
    const results = [];
    
    // Erfasse alle Masken
    for (const [index, mask] of L3_MASKS.entries()) {
      console.log(`\n${'='.repeat(70)}`);
      console.log(`[${index + 1}/${L3_MASKS.length}] ${mask.name}`);
      console.log('='.repeat(70));
      
      // Navigation
      const navSuccess = await navigateToMask(page, guiMap, mask);
      
      if (!navSuccess) {
        console.log(`   ❌ Navigation fehlgeschlagen`);
        results.push({ mask: mask.id, success: false });
        continue;
      }
      
      // Warte auf Laden
      await page.waitForTimeout(2000);
      
      // Screenshot
      const screenshot = await captureScreenshot(page, mask.id, CONFIG.outputDir);
      
      results.push({
        mask: mask.id,
        name: mask.name,
        screenshot,
        success: true,
        timestamp: new Date().toISOString()
      });
      
      console.log(`   ✅ Erfolgreich!`);
    }
    
    // Index speichern
    const indexPath = path.join(CONFIG.outputDir, 'index.json');
    fs.writeFileSync(indexPath, JSON.stringify({
      capturedAt: new Date().toISOString(),
      total: L3_MASKS.length,
      successful: results.filter(r => r.success).length,
      results
    }, null, 2));
    
    console.log(`\n✅ Index: ${indexPath}`);
    console.log(`🎉 ${results.filter(r => r.success).length}/${L3_MASKS.length} Masken erfasst!\n`);
    
  } catch (error) {
    console.error('\n❌ Fehler:', error);
  } finally {
    console.log('Browser bleibt offen für Inspektion...');
    // await browser.close();
  }
}

// CLI
if (require.main === module) {
  captureAllMasks();
}

module.exports = { clickGuacPct, navigateToMask, captureAllMasks };

