#!/usr/bin/env node

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
  if (normalized.startsWith('pages/')) {
    return '@/' + normalized;
  }
  return normalized;
}

// Konvertiert einen Modul-Specifier zu einem vorgeschlagenen Route-Pfad
function moduleToSuggestedPath(moduleSpecifier) {
  let routePath = moduleSpecifier.replace(/^@\/pages\//, '');
  
  if (routePath.endsWith('/index')) {
    routePath = routePath.slice(0, -6);
  }
  
  if (!routePath || routePath === 'index') {
    return '/';
  }
  
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
  
  const modulesWithAliases = allModules.filter(module => {
    return existingAliases.has(module);
  });
  
  console.log('✅ Module mit Aliases:', modulesWithAliases.length);
  console.log('⚠️  Module ohne Aliases:', modulesWithoutAliases.length);
  
  if (modulesWithoutAliases.length > 0) {
    console.log('\n📝 Hinzufügen fehlender Aliase...\n');
    
    const suggestions = modulesWithoutAliases
      .map(module => {
        let suggestedPath = moduleToSuggestedPath(module);
        if (isPortalModule(module)) {
          suggestedPath = 'portal/' + suggestedPath.replace(/^portal\//, '');
        }
        return {
          module,
          path: suggestedPath,
        };
      });
    
    const existingData = JSON.parse(fs.readFileSync(ALIASES_FILE, 'utf-8'));
    existingData.aliases.push(...suggestions);
    fs.writeFileSync(ALIASES_FILE, JSON.stringify(existingData, null, 2));
    
    console.log(`✅ Erfolgreich ${suggestions.length} Aliase hinzugefügt!`);
  } else {
    console.log('\n✅ Alle Module haben Aliase!\n');
  }
  
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
