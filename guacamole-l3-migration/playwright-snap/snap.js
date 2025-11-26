/**
 * VALEO-NeuroERP - L3 Screenshot Automation
 * Macht automatische Screenshots von L3-Masken via Guacamole
 */

import { chromium } from "playwright";
import fs from "fs/promises";
import path from "path";

// Konfiguration
const config = {
  guacUrl: process.env.GUAC_URL || "http://localhost:8080/guacamole",
  guacUser: process.env.GUAC_USER || "guacadmin",
  guacPass: process.env.GUAC_PASS || "guacadmin",
  outDir: process.env.OUT_DIR || "C:/guac-webtop/l3-screenshots",
  connectionName: process.env.CONNECTION_NAME || "L3-Windows",
  waitAfterConnect: parseInt(process.env.WAIT_SECONDS || "5") * 1000,
};

/**
 * Erstellt Output-Verzeichnis
 */
async function ensureDir(dir) {
  try {
    await fs.mkdir(dir, { recursive: true });
    console.log(`✅ Verzeichnis bereit: ${dir}`);
  } catch (e) {
    console.error(`❌ Fehler beim Erstellen des Verzeichnisses: ${e}`);
  }
}

/**
 * Screenshot von Guacamole Canvas
 */
async function captureGuacamoleScreen() {
  console.log("🚀 Starte L3-Screenshot-Automation...\n");
  
  await ensureDir(config.outDir);

  const browser = await chromium.launch({ 
    headless: true,
    args: ['--disable-dev-shm-usage']
  });
  
  try {
    const page = await browser.newPage();
    page.setDefaultTimeout(30000);

    // 1. Login-Seite laden
    console.log(`📡 Verbinde zu Guacamole: ${config.guacUrl}`);
    await page.goto(config.guacUrl);

    // 2. Login
    console.log(`🔐 Login als: ${config.guacUser}`);
    await page.fill('input[name="username"]', config.guacUser);
    await page.fill('input[name="password"]', config.guacPass);
    await page.click('button[type="submit"]');

    // 3. Warte auf Dashboard
    await page.waitForSelector('a.connection, a.list-group-item, .connection-group', { 
      timeout: 15000 
    });
    console.log("✅ Guacamole Dashboard geladen");

    // 4. Verbindung öffnen
    // Versuche spezifischen Connection-Namen zu finden
    let connectionLink = null;
    
    // Methode 1: Suche nach Connection-Namen
    try {
      connectionLink = await page.locator(`text=${config.connectionName}`).first();
      if (await connectionLink.count() > 0) {
        console.log(`🔗 Öffne Verbindung: ${config.connectionName}`);
        await connectionLink.click();
      }
    } catch (e) {
      // Methode 2: Erste verfügbare Verbindung
      console.log("⚠️ Spezifische Verbindung nicht gefunden, nutze erste verfügbare...");
      const links = await page.$$('a.connection, a.list-group-item');
      if (links.length === 0) {
        throw new Error("❌ Keine Verbindung gefunden!");
      }
      await links[0].click();
    }

    // 5. Warte auf Canvas (L3-Desktop wird geladen)
    console.log("⏳ Warte auf L3-Desktop...");
    await page.waitForSelector('canvas.display', { timeout: 30000 });
    
    // Extra-Wartezeit für vollständiges Rendering
    await page.waitForTimeout(config.waitAfterConnect);
    console.log("✅ L3-Desktop geladen");

    // 6. Screenshot vom Canvas
    const canvas = await page.$('canvas.display');
    
    if (!canvas) {
      throw new Error("❌ Guacamole Canvas nicht gefunden!");
    }

    // Timestamp für Dateiname
    const now = new Date();
    const timestamp = now.toISOString().replace(/[:.]/g, "-").slice(0, -5); // YYYY-MM-DDTHH-MM-SS
    const filename = `l3_mask_${timestamp}.png`;
    const filePath = path.join(config.outDir, filename);

    // Screenshot aufnehmen
    await canvas.screenshot({ 
      path: filePath,
      type: 'png',
      omitBackground: false
    });

    console.log(`\n📸 Screenshot gespeichert: ${filePath}`);
    
    // Metadaten speichern
    const metadata = {
      timestamp: now.toISOString(),
      url: config.guacUrl,
      connection: config.connectionName,
      filename: filename,
      size: (await fs.stat(filePath)).size,
    };
    
    const metaPath = path.join(config.outDir, `${filename}.json`);
    await fs.writeFile(metaPath, JSON.stringify(metadata, null, 2));
    console.log(`📝 Metadaten: ${metaPath}\n`);

    // Statistik
    const files = await fs.readdir(config.outDir);
    const screenshots = files.filter(f => f.endsWith('.png'));
    console.log(`📊 Gesamt-Screenshots: ${screenshots.length}`);

  } catch (error) {
    console.error(`❌ Fehler: ${error.message}`);
    throw error;
  } finally {
    await browser.close();
    console.log("✅ Browser geschlossen\n");
  }
}

// Script ausführen
captureGuacamoleScreen()
  .then(() => {
    console.log("🎉 Screenshot-Automation erfolgreich abgeschlossen!");
    process.exit(0);
  })
  .catch((error) => {
    console.error("❌ Fehler bei Screenshot-Automation:", error);
    process.exit(1);
  });

