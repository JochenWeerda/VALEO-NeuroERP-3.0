/**
 * L3 Single Screenshot
 * Macht einen Screenshot der aktuellen L3-Maske
 */

import { chromium } from "playwright";
import fs from "fs/promises";
import path from "path";

const config = {
  guacUrl: process.env.GUAC_URL || "http://localhost:8090/guacamole",
  guacUser: process.env.GUAC_USER || "guacadmin",
  guacPass: process.env.GUAC_PASS || "guacadmin",
  outDir: process.env.OUT_DIR || "../screenshots",
  waitSeconds: parseInt(process.env.WAIT_SECONDS || "5"),
};

async function captureScreen() {
  console.log("🚀 L3-Screenshot-Tool gestartet\n");
  
  // Verzeichnis erstellen
  await fs.mkdir(config.outDir, { recursive: true });

  const browser = await chromium.launch({ headless: false }); // headless=false für Debugging
  
  try {
    const page = await browser.newPage({ viewport: { width: 1920, height: 1080 } });
    page.setDefaultTimeout(30000);

    // 1. Guacamole Login
    console.log(`📡 Verbinde zu: ${config.guacUrl}`);
    await page.goto(config.guacUrl);

    console.log(`🔐 Login als: ${config.guacUser}`);
    await page.fill('input[name="username"]', config.guacUser);
    await page.fill('input[name="password"]', config.guacPass);
    await page.click('button[type="submit"]');

    // 2. Warte auf Dashboard und klicke erste Verbindung
    await page.waitForTimeout(2000);
    
    // Alle Connection-Links finden
    const connections = await page.$$('a[href*="/client/"]');
    
    if (connections.length === 0) {
      throw new Error("❌ Keine Verbindungen gefunden!");
    }
    
    console.log(`✅ ${connections.length} Verbindung(en) gefunden`);
    console.log(`🔗 Öffne erste Verbindung...`);
    await connections[0].click();

    // 3. Warte auf Canvas
    console.log("⏳ Warte auf L3-Desktop...");
    await page.waitForSelector('canvas.display', { timeout: 30000 });
    
    // Extra-Wartezeit für Rendering
    console.log(`⏱️ Warte ${config.waitSeconds}s für vollständiges Rendering...`);
    await page.waitForTimeout(config.waitSeconds * 1000);

    // 4. Screenshot
    const canvas = await page.$('canvas.display');
    
    if (!canvas) {
      throw new Error("❌ Canvas nicht gefunden!");
    }

    const timestamp = new Date().toISOString().replace(/[:.]/g, "-").slice(0, 19);
    const filename = `l3_${timestamp}.png`;
    const filepath = path.join(config.outDir, filename);

    console.log(`📸 Erstelle Screenshot...`);
    await canvas.screenshot({ 
      path: filepath,
      type: 'png'
    });

    // Metadaten
    const stats = await fs.stat(filepath);
    const metadata = {
      timestamp: new Date().toISOString(),
      filename: filename,
      filepath: filepath,
      filesize: stats.size,
      resolution: "auto",
      connection: config.guacUrl,
    };

    const metafile = filepath.replace('.png', '.json');
    await fs.writeFile(metafile, JSON.stringify(metadata, null, 2));

    console.log(`\n✅ Screenshot erfolgreich gespeichert!`);
    console.log(`   Datei: ${filepath}`);
    console.log(`   Größe: ${(stats.size / 1024).toFixed(2)} KB`);
    console.log(`   Meta:  ${metafile}\n`);

  } catch (error) {
    console.error(`\n❌ Fehler: ${error.message}\n`);
    throw error;
  } finally {
    await browser.close();
  }
}

// Ausführen
captureScreen()
  .then(() => process.exit(0))
  .catch(() => process.exit(1));

