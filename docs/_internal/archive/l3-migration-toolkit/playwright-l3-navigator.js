/**
 * L3 Vollautomatischer Navigator (Playwright)
 * 
 * Nutzt prozentuale Koordinaten aus CSV für fenstergrößen-unabhängige Navigation.
 * NO HANDS ON - vollautomatisch!
 */

const fs = require('fs');
const path = require('path');
const csv = require('csv-parse/sync');

// GUI-Map laden (aus CSV)
function loadGuiMap(csvPath) {
  const csvContent = fs.readFileSync(csvPath, 'utf-8');
  const records = csv.parse(csvContent, {
    columns: true,
    skip_empty_lines: true
  });
  
  const guiMap = {
    tabs: {},
    ribbon: {}
  };
  
  records.forEach(row => {
    const elem = {
      x_pct: parseFloat(row.x_pct),
      y_pct: parseFloat(row.y_pct),
      submenu_y_pct: row.submenu_y_pct ? parseFloat(row.submenu_y_pct) : null
    };
    
    if (row.group === 'tabs') {
      guiMap.tabs[row.name] = elem;
    } else if (row.group === 'ribbon') {
      guiMap.ribbon[row.name] = elem;
    }
  });
  
  return guiMap;
}

// Klick auf Guacamole Canvas (prozentuale Koordinaten)
async function clickOnGuacCanvas(page, xPct, yPct, elementName = 'Element') {
  const rect = await page.evaluate(() => {
    const c = document.querySelector('canvas');
    if (!c) return null;
    const r = c.getBoundingClientRect();
    return { x: r.x, y: r.y, width: r.width, height: r.height };
  });
  
  if (!rect) {
    console.error('❌ Canvas nicht gefunden');
    return false;
  }
  
  const x = Math.round(rect.x + rect.width * xPct / 100);
  const y = Math.round(rect.y + rect.height * yPct / 100);
  
  console.log(`   🖱️  Klicke '${elementName}' bei (${x}, ${y}) = (${xPct}%, ${yPct}%)`);
  
  // Klick via MouseEvent (robuster als page.mouse.click für Canvas)
  await page.evaluate(({ x, y }) => {
    const canvas = document.querySelector('canvas');
    const evt = new MouseEvent('click', {
      view: window,
      bubbles: true,
      cancelable: true,
      clientX: x,
      clientY: y
    });
    canvas.dispatchEvent(evt);
  }, { x, y });
  
  return true;
}

// L3-Masken Navigations-Definitionen
const L3_MASKS = [
  {
    id: 'kundenstamm',
    name: 'Kundenstamm',
    navigation: [
      { type: 'ribbon', element: 'Kunden', wait: 3000 }
    ]
  },
  {
    id: 'artikelstamm',
    name: 'Artikelstamm',
    navigation: [
      { type: 'ribbon', element: 'Artikel', wait: 3000 }
    ]
  },
  {
    id: 'crm',
    name: 'CRM Dashboard',
    navigation: [
      { type: 'ribbon', element: 'CRM', wait: 3000 }
    ]
  },
  {
    id: 'kalender',
    name: 'Kalender',
    navigation: [
      { type: 'ribbon', element: 'Kalender', wait: 2000 }
    ]
  },
  {
    id: 'angebot_auftrag',
    name: 'Angebot/Auftrag',
    navigation: [
      { type: 'ribbon', element: 'Angebot_Auftrag', wait: 3000 }
    ]
  },
  {
    id: 'einkauf',
    name: 'Einkauf-Verwaltung',
    navigation: [
      { type: 'ribbon', element: 'Einkauf_Waren', wait: 3000 }
    ]
  },
  {
    id: 'lieferanten',
    name: 'Lieferantenstamm',
    navigation: [
      { type: 'ribbon', element: 'Lieferanten', wait: 3000 }
    ]
  },
  {
    id: 'erfassung_menu',
    name: 'Erfassung (Menü)',
    navigation: [
      { type: 'tab', element: 'ERFASSUNG', wait: 1000 }
    ]
  },
  {
    id: 'abrechnung_menu',
    name: 'Abrechnung (Menü)',
    navigation: [
      { type: 'tab', element: 'ABRECHNUNG', wait: 1000 }
    ]
  },
  {
    id: 'lager_menu',
    name: 'Lager (Menü)',
    navigation: [
      { type: 'tab', element: 'LAGER', wait: 1000 }
    ]
  }
];

// Navigiere zu einer Maske
async function navigateToMask(page, guiMap, maskConfig) {
  console.log(`\n🧭 Navigiere zu: ${maskConfig.name}`);
  
  for (const step of maskConfig.navigation) {
    const elemMap = step.type === 'tab' ? guiMap.tabs : guiMap.ribbon;
    const elem = elemMap[step.element];
    
    if (!elem) {
      console.error(`   ❌ Element '${step.element}' nicht in GUI-Map gefunden`);
      return false;
    }
    
    const success = await clickOnGuacCanvas(
      page,
      elem.x_pct,
      elem.y_pct,
      step.element
    );
    
    if (!success) return false;
    
    await page.waitForTimeout(step.wait);
    
    // Falls Submenu vorhanden
    if (elem.submenu_y_pct) {
      console.log(`   🖱️  Klicke Submenu bei ${elem.submenu_y_pct}%`);
      await clickOnGuacCanvas(page, elem.x_pct, elem.submenu_y_pct, `${step.element} Submenu`);
      await page.waitForTimeout(1000);
    }
  }
  
  return true;
}

// Screenshot erstellen
async function captureScreenshot(page, maskId, outputDir) {
  const filename = `${maskId}.png`;
  const filepath = path.join(outputDir, filename);
  
  await page.screenshot({
    path: filepath,
    fullPage: false
  });
  
  console.log(`   ✅ Screenshot: ${filename}`);
  return filepath;
}

// Hauptfunktion: Erfasse alle Masken
async function captureAllMasks(page, csvPath, outputDir) {
  console.log('🚀 L3 Vollautomatische Masken-Erfassung\n');
  
  // Erstelle Output-Verzeichnis
  if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true });
  }
  
  // Lade GUI-Map
  console.log('📋 Lade GUI-Map...');
  const guiMap = loadGuiMap(csvPath);
  console.log(`✅ ${Object.keys(guiMap.tabs).length} Tabs, ${Object.keys(guiMap.ribbon).length} Ribbon-Elemente\n`);
  
  const results = [];
  
  for (const [index, mask] of L3_MASKS.entries()) {
    console.log(`\n${'='.repeat(70)}`);
    console.log(`[${index + 1}/${L3_MASKS.length}] Maske: ${mask.name}`);
    console.log('='.repeat(70));
    
    // Navigiere zu Maske
    const navSuccess = await navigateToMask(page, guiMap, mask);
    
    if (!navSuccess) {
      console.log(`   ❌ Navigation fehlgeschlagen`);
      results.push({ mask: mask.id, success: false });
      continue;
    }
    
    // Warte auf Maske-Laden
    await page.waitForTimeout(2000);
    
    // Screenshot
    const screenshot = await captureScreenshot(page, mask.id, outputDir);
    
    results.push({
      mask: mask.id,
      name: mask.name,
      screenshot: screenshot,
      success: true,
      timestamp: new Date().toISOString()
    });
    
    console.log(`   ✅ Erfolgreich: ${mask.name}`);
  }
  
  // Speichere Index
  const indexPath = path.join(outputDir, 'capture-index.json');
  fs.writeFileSync(indexPath, JSON.stringify({
    capturedAt: new Date().toISOString(),
    totalMasks: L3_MASKS.length,
    successfulCaptures: results.filter(r => r.success).length,
    results: results
  }, null, 2));
  
  console.log(`\n✅ Index gespeichert: ${indexPath}`);
  console.log(`\n🎉 ${results.filter(r => r.success).length}/${L3_MASKS.length} Masken erfolgreich erfasst!`);
  
  return results;
}

module.exports = {
  loadGuiMap,
  clickOnGuacCanvas,
  navigateToMask,
  captureScreenshot,
  captureAllMasks,
  L3_MASKS
};

