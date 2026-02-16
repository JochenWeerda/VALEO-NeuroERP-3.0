#!/usr/bin/env node
/**
 * Skript zur Identifikation fehlender Route-Aliase
 * 
 * Analysiert alle Page-Module und vergleicht sie mit vorhandenen Aliases
 * in route-aliases.json, um fehlende Aliase zu identifizieren.
 */

const fs = require('fs');
const path = require('path');

const FRONTEND_DIR = path.join(__dirname, '..', 'packages', 'frontend-web', 'src');
const PAGES_DIR = path.join(FRONTEND_DIR, 'pages');
const ALIASES_FILE = path.join(FRONTEND_DIR, 'app', 'route-aliases.json');

// Patterns, die ignoriert werden sollen
const IGNORE_PATTERNS = [
  /\/__tests__\//,
  /\.spec\.tsx$/,
  /\.test\.tsx$/,
  /\.stories\.tsx$/,
];

// Portal-Module werden separat behandelt
function isPortalModule(modulePath) {
  return modulePath.includes('/portal/');
}

// Konvertiert einen Dateipfad zu einem Modul-Specifier (@/pages/...)
function filePathToModuleSpecifier(filePath) {
  const relativePath = path.relative(FRONTEND_DIR, filePath);
  const normalized = relativePath.replace(/\\/g, '/').replace(/\.tsx$/, '');
  // Füge @/ hinzu, wenn es mit pages/ beginnt
  if (normalized.startsWith('pages/')) {
    return '@/' + normalized;
  }
  return normalized;
}

// Konvertiert einen Modul-Specifier zu einem vorgeschlagenen Route-Pfad
function moduleToSuggestedPath(moduleSpecifier) {
  let routePath = moduleSpecifier.replace(/^@\/pages\//, '');
  
  // Index-Dateien werden zu Root-Pfaden
  if (routePath.endsWith('/index')) {
    routePath = routePath.slice(0, -6);
  }
  
  // Leere Pfade werden zu Root
  if (!routePath || routePath === 'index') {
    return '/';
  }
  
  // Entferne "liste", "stamm" etc. für bessere URLs
  routePath = routePath
    .replace(/\/liste$/, '')
    .replace(/\/stamm$/, '')
    .replace(/-liste$/, '')
    .replace(/-stamm$/, '');
  
  return routePath;
}

// Liest vorhandene Aliase
function loadExistingAliases() {
  try {
    const content = fs.readFileSync(ALIASES_FILE, 'utf-8');
    const data = JSON.parse(content);
    const aliases = data.aliases || [];
    
    // Erstelle eine Map von Modul-Specifier zu Aliases
    const aliasMap = new Map();
    aliases.forEach(alias => {
      const module = alias.module;
      if (!aliasMap.has(module)) {
        aliasMap.set(module, []);
      }
      if (alias.path) {
        aliasMap.get(module).push(alias.path);
      }
    });
    
    return aliasMap;
  } catch (error) {
    console.error(`Fehler beim Lesen von ${ALIASES_FILE}:`, error.message);
    return new Map();
  }
}

// Rekursive Funktion zum Finden aller .tsx-Dateien
function findTsxFiles(dir, fileList = []) {
  const files = fs.readdirSync(dir);
  
  files.forEach(file => {
    const filePath = path.join(dir, file);
    const stat = fs.statSync(filePath);
    
    if (stat.isDirectory()) {
      findTsxFiles(filePath, fileList);
    } else if (file.endsWith('.tsx')) {
      fileList.push(filePath);
    }
  });
  
  return fileList;
}

// Findet alle Page-Module
function findAllPageModules() {
  const files = findTsxFiles(PAGES_DIR);
  
  return files
    .filter(file => {
      // Ignoriere Test- und Story-Dateien
      return !IGNORE_PATTERNS.some(pattern => pattern.test(file));
    })
    .map(file => filePathToModuleSpecifier(file))
    .filter(module => module.startsWith('@/pages/'));
}

// Hauptfunktion
function main() {
  console.log('🔍 Analysiere Route-Aliase...\n');
  
  const existingAliases = loadExistingAliases();
  const allModules = findAllPageModules();
  
  console.log(`📊 Gefundene Page-Module: ${allModules.length}`);
  console.log(`📋 Vorhandene Aliase: ${existingAliases.size}\n`);
  
  // Finde Module ohne Aliase
  const modulesWithoutAliases = allModules.filter(module => {
    return !existingAliases.has(module);
  });
  
  // Finde Module mit Aliases
  const modulesWithAliases = allModules.filter(module => {
    return existingAliases.has(module);
  });
  
  console.log('✅ Module mit Aliases:', modulesWithAliases.length);
  console.log('⚠️  Module ohne Aliases:', modulesWithoutAliases.length);
  
  if (modulesWithoutAliases.length > 0) {
    console.log('\n📝 Vorschläge für fehlende Aliase:\n');
    
    const suggestions = modulesWithoutAliases
      .map(module => {
        const suggestedPath = moduleToSuggestedPath(module);
        return {
          module,
          suggestedPath,
          isPortal: isPortalModule(module),
        };
      })
      .sort((a, b) => {
        // Portal-Module zuletzt
        if (a.isPortal !== b.isPortal) {
          return a.isPortal ? 1 : -1;
        }
        return a.module.localeCompare(b.module);
      });
    
    // Gruppiere nach Portal/Non-Portal
    const mainApp = suggestions.filter(s => !s.isPortal);
    const portal = suggestions.filter(s => s.isPortal);
    
    if (mainApp.length > 0) {
      console.log('📦 Hauptanwendung:');
      mainApp.forEach(({ module, suggestedPath }) => {
        console.log(`  {
    "module": "${module}",
    "path": "${suggestedPath}"
  },`);
      });
    }
    
    if (portal.length > 0) {
      console.log('\n🌐 Portal:');
      portal.forEach(({ module, suggestedPath }) => {
        console.log(`  {
    "module": "${module}",
    "path": "portal/${suggestedPath.replace(/^portal\//, '')}"
  },`);
      });
    }
    
    console.log(`\n💡 Insgesamt ${suggestions.length} fehlende Aliase gefunden.`);
    console.log('   Diese können manuell zu route-aliases.json hinzugefügt werden.\n');
  } else {
    console.log('\n✅ Alle Module haben Aliase!\n');
  }
  
  // Prüfe auf ungültige Aliase (Module existieren nicht)
  const invalidAliases = [];
  existingAliases.forEach((paths, module) => {
    if (!allModules.includes(module)) {
      invalidAliases.push({ module, paths });
    }
  });
  
  if (invalidAliases.length > 0) {
    console.log('⚠️  Ungültige Aliase (Module existieren nicht):');
    invalidAliases.forEach(({ module, paths }) => {
      console.log(`  - ${module} (Pfade: ${paths.join(', ')})`);
    });
    console.log();
  }
}

try {
  main();
} catch (error) {
  console.error('Fehler:', error);
  process.exit(1);
}

