#!/usr/bin/env python
"""
Migrations-Skript für den EnhancedCacheManager

Dieses Skript hilft bei der automatischen Migration von API-Modulen
vom alten CacheManager zum neuen EnhancedCacheManager mit Tag-basierter
Invalidierung und verbesserten Funktionen.

Verwendung:
    python migrate_to_enhanced_cache.py <Dateipfad>
    python migrate_to_enhanced_cache.py --all
"""

import os
import sys
import re
import logging
import argparse
from typing import List, Dict, Any, Optional, Tuple

# Logging einrichten
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Konstanten
API_DIR = os.path.join("backend", "api")
OLD_IMPORT = "from cache_manager import cache"
NEW_IMPORT = "from enhanced_cache_manager import cache"
LOGGING_IMPORT = "import logging"
DECORATOR_PATTERN = r"@cache\.cached\(ttl=(\d+)\)"
NEW_DECORATOR_TEMPLATE = '@cache.cached(ttl={ttl}, tags={tags})'
LOGGER_DEFINITION = "logger = logging.getLogger(__name__)"

# Tag-Definitionen für verschiedene API-Module
API_TAGS = {
    "charges_api.py": {
        "module": "charges",
        "entity": "charge",
        "additional_tags": ["references"],
    },
    "articles_api.py": {
        "module": "articles",
        "entity": "article",
        "additional_tags": ["inventory", "pricing"],
    },
    "stock_charges_api.py": {
        "module": "stock",
        "entity": "stock",
        "additional_tags": ["inventory", "locations"],
    },
    "quality_api.py": {
        "module": "quality",
        "entity": "quality",
        "additional_tags": ["reports", "monitoring"],
    },
    "production_api.py": {
        "module": "production",
        "entity": "production",
        "additional_tags": ["orders", "scheduling"],
    },
    "inventory_api.py": {
        "module": "inventory",
        "entity": "inventory",
        "additional_tags": ["locations", "movements"],
    },
}

# Standard-Tags für alle API-Module
DEFAULT_TAGS = ["list", "stats", "details"]

def parse_arguments() -> argparse.Namespace:
    """Kommandozeilenargumente verarbeiten"""
    parser = argparse.ArgumentParser(
        description="Migriert API-Module zum EnhancedCacheManager"
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "file_path", 
        nargs="?", 
        help="Pfad zur API-Datei, die migriert werden soll"
    )
    group.add_argument(
        "--all", 
        action="store_true", 
        help="Alle API-Module migrieren"
    )
    parser.add_argument(
        "--dry-run", 
        action="store_true", 
        help="Änderungen anzeigen, ohne sie zu speichern"
    )
    return parser.parse_args()

def get_api_files() -> List[str]:
    """Gibt eine Liste aller API-Dateien zurück"""
    api_files = []
    for file in os.listdir(API_DIR):
        if file.endswith("_api.py"):
            api_files.append(os.path.join(API_DIR, file))
    return api_files

def detect_endpoints(content: str) -> List[Dict[str, Any]]:
    """Erkennt FastAPI-Endpunkte in der Datei"""
    
    # Regex-Muster für FastAPI-Endpunkte
    endpoint_pattern = r'@router\.(get|post|put|delete|patch)\(["\']([^"\']+)["\']\)[^\n]*\n(?:@cache\.cached\([^\)]*\)\n)?async def ([^\(]+)\('
    
    endpoints = []
    for match in re.finditer(endpoint_pattern, content, re.MULTILINE):
        method, path, func_name = match.groups()
        
        # Überprüfen, ob ein Cache-Dekorator vorhanden ist
        start_pos = match.start()
        line_before = content[:start_pos].rfind("\n")
        has_cache = "@cache.cached" in content[line_before:start_pos]
        
        # Parameter aus dem Pfad extrahieren
        path_params = re.findall(r'{([^}]+)}', path)
        
        endpoints.append({
            "method": method,
            "path": path,
            "function": func_name,
            "has_cache": has_cache,
            "path_params": path_params
        })
    
    return endpoints

def generate_tags_for_endpoint(endpoint: Dict[str, Any], api_tags: Dict[str, Any]) -> List[str]:
    """Generiert Tags für einen Endpunkt basierend auf dem Pfad und der Methode"""
    tags = []
    
    # Modul-Tag hinzufügen
    tags.append(api_tags["module"])
    
    # Methode berücksichtigen
    if endpoint["method"] == "get":
        if not endpoint["path_params"]:
            # Listen-Endpunkt
            tags.append("list")
        else:
            # Detail-Endpunkt
            tags.append("details")
            
            # Entity-Tag mit ID hinzufügen
            for param in endpoint["path_params"]:
                if "id" in param.lower():
                    tags.append(f"{api_tags['entity']}:{{{param}}}")
    
    # Zusätzliche Tags basierend auf dem Pfad
    path_lower = endpoint["path"].lower()
    
    # Stats-Endpunkte
    if "stats" in path_lower or "statistics" in path_lower:
        tags.append("stats")
    
    # Spezifische Tags aus dem API-Modul
    for tag in api_tags["additional_tags"]:
        if tag in path_lower:
            tags.append(tag)
    
    return tags

def migrate_file(file_path: str, dry_run: bool = False) -> bool:
    """Migriert eine API-Datei zum EnhancedCacheManager"""
    try:
        # Dateinamen extrahieren
        filename = os.path.basename(file_path)
        
        # Tags für dieses API-Modul
        module_tags = API_TAGS.get(filename, {
            "module": filename.replace("_api.py", ""),
            "entity": filename.replace("_api.py", "").rstrip("s"),
            "additional_tags": DEFAULT_TAGS
        })
        
        logger.info(f"Migriere Datei: {file_path}")
        
        # Datei lesen
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Sicherstellen, dass wir nur einmal migrieren
        if NEW_IMPORT in content:
            logger.warning(f"Datei wurde bereits migriert: {file_path}")
            return False
        
        # Änderungen verfolgen
        changes = []
        
        # Import ändern
        if OLD_IMPORT in content:
            new_content = content.replace(OLD_IMPORT, NEW_IMPORT)
            changes.append(f"Import geändert: {OLD_IMPORT} -> {NEW_IMPORT}")
        else:
            logger.warning(f"Alter Import nicht gefunden in: {file_path}")
            new_content = content
        
        # Logging hinzufügen, falls nicht vorhanden
        if LOGGING_IMPORT not in new_content:
            import_section_end = new_content.find("\n\n", new_content.find("import"))
            if import_section_end != -1:
                new_content = new_content[:import_section_end] + f"\n{LOGGING_IMPORT}" + new_content[import_section_end:]
                changes.append(f"Logging-Import hinzugefügt")
        
        # Logger-Definition hinzufügen, falls nicht vorhanden
        if LOGGER_DEFINITION not in new_content and "router = APIRouter()" in new_content:
            router_pos = new_content.find("router = APIRouter()")
            if router_pos != -1:
                line_end = new_content.find("\n", router_pos)
                new_content = new_content[:line_end+1] + f"{LOGGER_DEFINITION}\n" + new_content[line_end+1:]
                changes.append(f"Logger-Definition hinzugefügt")
        
        # Endpunkte erkennen
        endpoints = detect_endpoints(new_content)
        logger.info(f"Gefundene Endpunkte: {len(endpoints)}")
        
        # Cache-Dekoratoren aktualisieren
        for match in re.finditer(DECORATOR_PATTERN, new_content):
            ttl = match.group(1)
            
            # Position des zugehörigen Endpunkts finden
            decorator_pos = match.start()
            next_line_pos = new_content.find("\n", decorator_pos) + 1
            
            # Endpunkt nach dem Dekorator finden
            endpoint_line = new_content[next_line_pos:new_content.find("\n", next_line_pos)]
            endpoint_match = None
            
            for ep in endpoints:
                if f"async def {ep['function']}" in endpoint_line:
                    endpoint_match = ep
                    break
            
            if endpoint_match:
                # Tags für diesen Endpunkt generieren
                tags = generate_tags_for_endpoint(endpoint_match, module_tags)
                
                # Neuen Dekorator erstellen
                tags_str = str(tags).replace("'", '"')
                new_decorator = NEW_DECORATOR_TEMPLATE.format(ttl=ttl, tags=tags_str)
                
                # Dekorator ersetzen
                old_decorator = match.group(0)
                new_content = new_content.replace(old_decorator, new_decorator)
                
                changes.append(f"Dekorator aktualisiert für {endpoint_match['function']}: {old_decorator} -> {new_decorator}")
        
        # Cache-Invalidierung für Mutations-Endpunkte hinzufügen
        for ep in endpoints:
            if ep["method"] in ["post", "put", "delete", "patch"] and not ep["has_cache"]:
                # Funktion finden
                func_pattern = f"async def {ep['function']}\\([^)]*\\):[^\\n]*\\n"
                func_match = re.search(func_pattern, new_content)
                
                if func_match:
                    # Nach dem return-Statement suchen
                    func_start = func_match.end()
                    func_end = None
                    
                    # Nächste Funktion oder Dateiende suchen
                    next_func = re.search(r"async def [^\(]+\(", new_content[func_start:])
                    if next_func:
                        func_end = func_start + next_func.start()
                    else:
                        func_end = len(new_content)
                    
                    func_body = new_content[func_start:func_end]
                    
                    # Return-Statement finden
                    return_match = re.search(r"(\s+)return\s+", func_body)
                    
                    if return_match:
                        indentation = return_match.group(1)
                        return_pos = func_start + return_match.start()
                        
                        # Cache-Invalidierungscode erstellen
                        invalidation_code = f"\n{indentation}# Cache-Invalidierung\n"
                        
                        # ID-Parameter finden
                        id_params = [p for p in ep["path_params"] if "id" in p.lower()]
                        
                        if id_params:
                            for param in id_params:
                                invalidation_code += f"{indentation}cache.invalidate_tag(f\"{module_tags['entity']}:{{{param}}}\")\n"
                        
                        # Modul-Tag invalidieren
                        invalidation_code += f"{indentation}cache.invalidate_tag(\"{module_tags['module']}\")\n"
                        
                        # Code einfügen
                        new_content = new_content[:return_pos] + invalidation_code + new_content[return_pos:]
                        changes.append(f"Cache-Invalidierung hinzugefügt für {ep['function']}")
        
        # Cache-Stats-Endpunkt hinzufügen, falls nicht vorhanden
        if not any(ep["path"].endswith("/cache-stats") for ep in endpoints):
            # Position für den neuen Endpunkt finden (nach dem letzten Endpunkt)
            last_endpoint_pos = 0
            for ep in endpoints:
                func_pattern = f"async def {ep['function']}\\([^)]*\\):[^\\n]*\\n"
                func_match = re.search(func_pattern, new_content)
                if func_match:
                    func_end = new_content.find("\n\n", func_match.end())
                    if func_end > last_endpoint_pos:
                        last_endpoint_pos = func_end
            
            if last_endpoint_pos > 0:
                # Einrückung ermitteln
                last_lines = new_content[:last_endpoint_pos].split("\n")
                if last_lines:
                    indentation = ""
                    for char in last_lines[-1]:
                        if char in [" ", "\t"]:
                            indentation += char
                        else:
                            break
                else:
                    indentation = "    "  # Standard-Einrückung
                
                # Neuen Endpunkt erstellen
                module_name = module_tags["module"]
                stats_endpoint = f"\n\n@router.get(\"/api/v1/{module_name}/cache-stats\")\nasync def get_{module_name}_cache_stats():\n{indentation}\"\"\"Gibt Statistiken zum {module_name.capitalize()}-Cache zurück\"\"\"\n{indentation}return cache.get_stats()\n"
                
                # Endpunkt einfügen
                new_content = new_content[:last_endpoint_pos] + stats_endpoint + new_content[last_endpoint_pos:]
                changes.append(f"Cache-Stats-Endpunkt hinzugefügt: get_{module_name}_cache_stats")
        
        # Änderungen anzeigen
        for change in changes:
            logger.info(f"  - {change}")
        
        # Datei speichern, wenn nicht im Dry-Run-Modus
        if not dry_run and changes:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(new_content)
            logger.info(f"Datei erfolgreich migriert: {file_path}")
        elif dry_run:
            logger.info(f"Dry-Run: Änderungen werden nicht gespeichert")
        
        return bool(changes)
    
    except Exception as e:
        logger.error(f"Fehler bei der Migration von {file_path}: {str(e)}")
        return False

def main():
    """Hauptfunktion"""
    args = parse_arguments()
    
    if args.all:
        # Alle API-Dateien migrieren
        api_files = get_api_files()
        if not api_files:
            logger.error(f"Keine API-Dateien gefunden in: {API_DIR}")
            sys.exit(1)
        
        successful = 0
        for file_path in api_files:
            if migrate_file(file_path, args.dry_run):
                successful += 1
        
        logger.info(f"Migration abgeschlossen: {successful}/{len(api_files)} Dateien erfolgreich migriert")
    else:
        # Einzelne Datei migrieren
        if not os.path.exists(args.file_path):
            logger.error(f"Datei nicht gefunden: {args.file_path}")
            sys.exit(1)
        
        if migrate_file(args.file_path, args.dry_run):
            logger.info(f"Migration erfolgreich: {args.file_path}")
        else:
            logger.warning(f"Keine Änderungen vorgenommen: {args.file_path}")

if __name__ == "__main__":
    main() 