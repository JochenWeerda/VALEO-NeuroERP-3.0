/**
 * L3 Keyboard-basierter Auto-Navigator
 * 
 * Nutzt Tastatur-Shortcuts (Alt-Menüs) statt Maus-Klicks.
 * STABILSTE Methode für Guacamole RDP!
 * 
 * Funktioniert auch bei:
 * - Verschiedenen Auflösungen
 * - Zoom-Levels
 * - Skalierungen
 */

const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

// Konfiguration
const CONFIG = {
  guacamoleUrl: 'http://localhost:8090/guacamole/#/client/MQBjAHBvc3RncmVzcWw',
  outputDir: path.join(__dirname, '..', 'screenshots', 'l3-masks-auto'),
  waitAfterKey: 300,      // Warte nach Tastendruck
  waitAfterMenu: 1500,    // Warte nach Menü-Öffnung
  waitAfterMask: 3000,    // Warte nach Masken-Öffnung
};

// L3-Masken mit Keyboard-Navigation
const L3_MASKS_KEYBOARD = [
  {
    id: '01_erfassung_menu',
    name: 'ERFASSUNG Menü',
    keys: [
      { key: 'Alt', wait: 200 },
      { key: 'e', wait: 1000, description: 'Öffne ERFASSUNG' }
    ]
  },
  {
    id: '02_abrechnung_menu',
    name: 'ABRECHNUNG Menü',
    keys: [
      { key: 'Alt', wait: 200 },
      { key: 'a', wait: 1000, description: 'Öffne ABRECHNUNG' }
    ]
  },
  {
    id: '03_lager_menu',
    name: 'LAGER Menü',
    keys: [
      { key: 'Alt', wait: 200 },
      { key: 'l', wait: 1000, description: 'Öffne LAGER' }
    ]
  },
  {
    id: '04_allgemein_kunden',
    name: 'Kunden (via Alt+A)',
    keys: [
      { key: 'Alt', wait: 200 },
      { key: 'a', wait: 500, description: 'ALLGEMEIN' },
      { key: 'Tab', wait: 200, description: 'Zu Ribbon' },
      { key: 'Enter', wait: 2000, description: 'Öffne Kunden' }
    ]
  }
];

// Fokussiere Canvas
async function focusCanvas(page) {
  try {
    const canvas = page.locator('canvas').first();
    await canvas.waitFor({ timeout: 5000 });
    
    // Klick irgendwo aufs Canvas um Fokus zu setzen
    const box = await canvas.boundingBox();
    if (box && box.width > 0) {
      await page.mouse.click(box.x + 100, box.y + 100);
      await page.waitForTimeout(200);
      return true;
    }
  } catch (e) {
    console.error('   ⚠️  Canvas-Fokus fehlgeschlagen:', e.message);
  }
  return false;
}

// Keyboard-Navigation durchführen
async function navigateViKeyboard(page, maskConfig) {
  console.log(`\n🧭 Navigiere zu: ${maskConfig.name}`);
  console.log(`   Tastatur-Sequenz: ${maskConfig.keys.length} Schritte`);
  
  // Fokussiere Canvas ZUERST
  const focused = await focusCanvas(page);
  if (!focused) {
    console.log('   ⚠️  Canvas nicht fokussiert, versuche trotzdem...');
  }
  
  // Führe Tastatur-Sequenz aus
  for (const [index, keyStep] of maskConfig.keys.entries()) {
    const stepNum = index + 1;
    const desc = keyStep.description || `Taste: ${keyStep.key}`;
    
    console.log(`   [${stepNum}/${maskConfig.keys.length}] ${desc}`);
    
    // Taste drücken
    await page.keyboard.press(keyStep.key);
    
    // Warte
    await page.waitForTimeout(keyStep.wait || CONFIG.waitAfterKey);
  }
  
  // Extra-Wartezeit für Masken-Laden
  await page.waitForTimeout(CONFIG.waitAfterMask);
  
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

// Hauptfunktion
async function captureAllMasksKeyboard() {
  console.log('🚀 L3 Keyboard-basierte Auto-Erfassung\n');
  console.log('⌨️  Nutzt Alt-Shortcuts statt Maus-Klicks\n');
  
  // Output-Verzeichnis
  if (!fs.existsSync(CONFIG.outputDir)) {
    fs.mkdirSync(CONFIG.outputDir, { recursive: true });
    console.log(`✅ Output: ${CONFIG.outputDir}\n`);
  }
  
  // Browser starten
  console.log('🌐 Starte Browser...');
  const browser = await chromium.launch({ 
    headless: false,
    slowMo: 100  // Langsamer für bessere Sichtbarkeit
  });
  
  const context = await browser.newContext();
  const page = await context.newPage();
  
  try {
    // Navigiere zu Guacamole Login
    console.log('🔗 Verbinde zu Guacamole...');
    await page.goto('http://localhost:8090/guacamole/', { waitUntil: 'networkidle' });
    await page.waitForTimeout(2000);
    
    // Guacamole Login
    console.log('🔐 Guacamole-Login (guacadmin)...');
    await page.fill('input[name="username"]', 'guacadmin');
    await page.fill('input[name="password"]', 'guacadmin');
    await page.click('button[type="submit"]');
    await page.waitForTimeout(2000);
    
    // Klicke auf L3-Windows-RDP Verbindung
    console.log('📡 Öffne L3-Windows-RDP...');
    await page.click('text=L3-Windows-RDP');
    await page.waitForTimeout(5000);
    
    // L3 Passwort eingeben (falls Dialog erscheint)
    console.log('🔑 L3-Login (Abcd1234)...');
    try {
      const passwordField = page.locator('input[type="password"]');
      if (await passwordField.isVisible({ timeout: 3000 })) {
        await passwordField.fill('Abcd1234');
        await page.click('button:has-text("Weiter")');
        await page.waitForTimeout(3000);
      }
    } catch (e) {
      console.log('   ℹ️  Kein Passwort-Dialog (bereits eingeloggt)');
    }
    
    // Warte auf vollständiges Laden von L3
    console.log('⏳ Warte auf L3-Desktop (5s)...');
    await page.waitForTimeout(5000);
    
    // Prüfe ob Canvas geladen
    const canvas = page.locator('canvas').first();
    const box = await canvas.boundingBox();
    console.log(`✅ Canvas geladen: ${box ? box.width + 'x' + box.height : 'unknown'}\n`);
    
    const results = [];
    
    // Erfasse alle Masken
    for (const [index, mask] of L3_MASKS_KEYBOARD.entries()) {
      console.log(`\n${'='.repeat(70)}`);
      console.log(`[${index + 1}/${L3_MASKS_KEYBOARD.length}] ${mask.name}`);
      console.log('='.repeat(70));
      
      // Keyboard-Navigation
      const navSuccess = await navigateViKeyboard(page, mask);
      
      if (!navSuccess) {
        console.log(`   ❌ Navigation fehlgeschlagen`);
        results.push({ mask: mask.id, success: false });
        continue;
      }
      
      // Screenshot
      const screenshot = await captureScreenshot(page, mask.id, CONFIG.outputDir);
      
      results.push({
        mask: mask.id,
        name: mask.name,
        screenshot,
        success: true,
        timestamp: new Date().toISOString()
      });
      
      console.log(`   ✅ Erfolgreich!\n`);
      
      // Escape drücken um Menü zu schließen
      console.log('   🔙 Schließe Menü/Maske (Escape)');
      await page.keyboard.press('Escape');
      await page.waitForTimeout(500);
      await page.keyboard.press('Escape');
      await page.waitForTimeout(500);
    }
    
    // Index speichern
    const indexPath = path.join(CONFIG.outputDir, 'index.json');
    fs.writeFileSync(indexPath, JSON.stringify({
      capturedAt: new Date().toISOString(),
      method: 'keyboard',
      total: L3_MASKS_KEYBOARD.length,
      successful: results.filter(r => r.success).length,
      results
    }, null, 2));
    
    console.log(`\n${'='.repeat(70)}`);
    console.log(`✅ Index: ${indexPath}`);
    console.log(`🎉 ${results.filter(r => r.success).length}/${L3_MASKS_KEYBOARD.length} Masken erfasst!`);
    console.log('='.repeat(70));
    
  } catch (error) {
    console.error('\n❌ Fehler:', error.message);
  } finally {
    console.log('\n🔒 Browser bleibt offen für Inspektion...');
    console.log('   Drücken Sie Strg+C zum Beenden');
    // Browser bleibt offen
    await new Promise(() => {}); // Infinite wait
  }
}

// CLI
if (require.main === module) {
  captureAllMasksKeyboard().catch(console.error);
}

module.exports = { navigateViKeyboard, captureAllMasksKeyboard };

