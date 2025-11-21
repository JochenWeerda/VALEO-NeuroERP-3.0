/**
 * Interaktive L3-Masken-Erfassung
 * 
 * Erlaubt manuelle Navigation durch L3, während Screenshots automatisch erstellt werden.
 * Drücken Sie Tastenkürzel, um Screenshots zu erstellen und Koordinaten zu loggen.
 */

const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');
const readline = require('readline');

const CONFIG = {
  guacamoleUrl: 'http://localhost:8090/guacamole/***REMOVED***/client/MQBjAHBvc3RncmVzcWw',
  outputDir: path.join(__dirname, '../screenshots/l3-masks'),
};

let screenshotCounter = 1;
const capturedMasks = [];

// Readline-Interface für Benutzer-Eingaben
const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout
});

function ensureOutputDir() {
  if (!fs.existsSync(CONFIG.outputDir)) {
    fs.mkdirSync(CONFIG.outputDir, { recursive: true });
  }
}

function prompt(question) {
  return new Promise((resolve) => {
    rl.question(question, (answer) => {
      resolve(answer.trim());
    });
  });
}

async function captureCurrentScreen(page, maskName) {
  const filename = `${String(screenshotCounter).padStart(2, '0')}_${maskName.toLowerCase().replace(/[^a-z0-9]/g, '-')}.png`;
  const filepath = path.join(CONFIG.outputDir, filename);
  
  await page.screenshot({
    path: filepath,
    fullPage: false,
  });
  
  const maskInfo = {
    id: screenshotCounter,
    name: maskName,
    filename: filename,
    timestamp: new Date().toISOString(),
  };
  
  capturedMasks.push(maskInfo);
  screenshotCounter++;
  
  console.log(`   ✅ Screenshot gespeichert: ${filename}`);
  return maskInfo;
}

async function interactiveCapture() {
  console.log('🚀 Interaktive L3-Masken-Erfassung\n');
  console.log('📋 Anleitung:');
  console.log('   1. Navigieren Sie manuell durch L3 im Browser');
  console.log('   2. Geben Sie den Masken-Namen ein und drücken Sie Enter für Screenshot');
  console.log('   3. Geben Sie "exit" ein zum Beenden\n');
  
  ensureOutputDir();
  
  const browser = await chromium.launch({
    headless: false,
    slowMo: 50,
  });
  
  const context = await browser.newContext({
    viewport: { width: 1920, height: 1080 },
  });
  
  const page = await context.newPage();
  
  try {
    console.log('🔗 Verbinde zu Guacamole RDP...\n');
    await page.goto(CONFIG.guacamoleUrl, { waitUntil: 'networkidle' });
    await page.waitForTimeout(3000);
    
    console.log('✅ Verbunden! Browser bleibt geöffnet für manuelle Navigation.\n');
    
    // Hauptschleife
    while (true) {
      const input = await prompt('\n📸 Maske-Name (oder "exit"): ');
      
      if (input.toLowerCase() === 'exit') {
        console.log('\n👋 Beende Erfassung...');
        break;
      }
      
      if (!input) {
        console.log('⚠️  Bitte einen Masken-Namen eingeben.');
        continue;
      }
      
      console.log(`   📸 Erstelle Screenshot: ${input}`);
      await captureCurrentScreen(page, input);
    }
    
    // Speichere Index
    const indexPath = path.join(CONFIG.outputDir, 'index.json');
    fs.writeFileSync(
      indexPath,
      JSON.stringify({
        generatedAt: new Date().toISOString(),
        totalMasks: capturedMasks.length,
        masks: capturedMasks,
      }, null, 2)
    );
    
    console.log(`\n✅ Index gespeichert: index.json`);
    console.log(`🎉 ${capturedMasks.length} Screenshots erstellt!\n`);
    
    // Zeige Zusammenfassung
    console.log('📋 Erfasste Masken:');
    capturedMasks.forEach((mask, idx) => {
      console.log(`   ${idx + 1}. ${mask.name} (${mask.filename})`);
    });
    
  } catch (error) {
    console.error('\n❌ Fehler:', error);
  } finally {
    rl.close();
    console.log('\n🔒 Browser schließen...');
    await browser.close();
  }
}

// CLI-Ausführung
if (require.main === module) {
  interactiveCapture();
}

module.exports = { interactiveCapture };

