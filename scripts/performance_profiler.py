#!/usr/bin/env python
"""
Performance Profiler für API-Module

Dieses Skript führt Performance-Tests für API-Module durch und identifiziert
Engpässe, insbesondere bei Datenbankabfragen.
"""

import argparse
import json
import time
import os
import sys
import requests
import statistics
import logging
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

# Projektpfad hinzufügen, um Backend-Importe zu ermöglichen
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Logger konfigurieren
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("perf_profiler.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("perf_profiler")

# API-Host (Standard: localhost)
API_HOST = "http://localhost:8000"

# Liste der API-Module und ihrer Endpunkte für den Test
API_ENDPOINTS = {
    "articles": [
        {"method": "GET", "path": "/api/v1/artikel", "name": "Alle Artikel abrufen"},
        {"method": "GET", "path": "/api/v1/artikel/l3format", "name": "Artikel im L3-Format"},
        {"method": "GET", "path": "/api/v1/artikel/1", "name": "Artikel nach ID"},
        {"method": "GET", "path": "/api/v1/artikel/search?bezeichnung=Stuhl", "name": "Artikelsuche"},
        {"method": "GET", "path": "/api/v1/artikel/statistik", "name": "Artikelstatistik"}
    ],
    "charges": [
        {"method": "GET", "path": "/api/v1/charge", "name": "Alle Chargen abrufen"},
        {"method": "GET", "path": "/api/v1/charge/1", "name": "Charge nach ID"},
        {"method": "GET", "path": "/api/v1/charge/1/vorwaerts", "name": "Vorwärtsverfolgung"},
        {"method": "GET", "path": "/api/v1/charge/1/rueckwaerts", "name": "Rückwärtsverfolgung"},
        {"method": "GET", "path": "/api/v1/charge/search?status=freigegeben", "name": "Chargensuche"}
    ],
    "inventory": [
        {"method": "GET", "path": "/api/v1/inventory", "name": "Alle Inventuren abrufen"},
        {"method": "GET", "path": "/api/v1/inventory/1", "name": "Inventur nach ID"},
        {"method": "GET", "path": "/api/v1/inventory/1/positions", "name": "Inventurpositionen"},
        {"method": "GET", "path": "/api/v1/inventory/statistics", "name": "Inventurstatistiken"}
    ],
    "quality": [
        {"method": "GET", "path": "/api/v1/qs/monitoring", "name": "QS-Monitoring"},
        {"method": "GET", "path": "/api/v1/qs/events", "name": "QS-Ereignisse"},
        {"method": "GET", "path": "/api/v1/qs/reports", "name": "QS-Berichte"},
        {"method": "GET", "path": "/api/v1/qs/certificates", "name": "QS-Zertifikate"}
    ],
    "production": [
        {"method": "GET", "path": "/api/v1/produktion/orders", "name": "Produktionsaufträge"},
        {"method": "GET", "path": "/api/v1/produktion/orders/1", "name": "Produktionsauftrag nach ID"},
        {"method": "GET", "path": "/api/v1/produktion/statistics", "name": "Produktionsstatistiken"},
        {"method": "GET", "path": "/api/v1/produktion/processes", "name": "Produktionsprozesse"}
    ],
    "system": [
        {"method": "GET", "path": "/api/system/info", "name": "Systeminformationen"},
        {"method": "GET", "path": "/api/system/status", "name": "Systemstatus"},
        {"method": "GET", "path": "/api/system/cache/stats", "name": "Cache-Statistiken"}
    ]
}

def measure_response_time(method, url, iterations=10):
    """Misst die Antwortzeit eines API-Endpunkts über mehrere Iterationen"""
    response_times = []
    errors = 0
    headers = {"X-Profiling": "enabled"}  # Header für detailliertes Profiling aktivieren
    
    logger.info(f"Teste {method} {url} ({iterations} Iterationen)")
    
    for i in range(iterations):
        try:
            start_time = time.time()
            
            if method == "GET":
                response = requests.get(url, headers=headers, timeout=10)
            elif method == "POST":
                response = requests.post(url, json={}, headers=headers, timeout=10)
            elif method == "PUT":
                response = requests.put(url, json={}, headers=headers, timeout=10)
            elif method == "DELETE":
                response = requests.delete(url, headers=headers, timeout=10)
            else:
                logger.error(f"Unbekannte HTTP-Methode: {method}")
                return None
            
            end_time = time.time()
            duration = (end_time - start_time) * 1000  # in Millisekunden
            
            if response.status_code < 400:  # Erfolgreiche Antwort
                response_times.append(duration)
                logger.debug(f"  Iteration {i+1}: {duration:.2f} ms")
                
                # Extrahiere DB-Statistiken, falls vorhanden
                db_stats = None
                try:
                    if "X-DB-Stats" in response.headers:
                        db_stats = json.loads(response.headers["X-DB-Stats"])
                except:
                    pass
                    
            else:
                logger.warning(f"  Fehler bei {method} {url}: Status {response.status_code}")
                errors += 1
        
        except Exception as e:
            logger.error(f"  Fehler bei {method} {url}: {str(e)}")
            errors += 1
    
    # Ergebnisse berechnen
    if response_times:
        avg_time = statistics.mean(response_times)
        median_time = statistics.median(response_times)
        min_time = min(response_times)
        max_time = max(response_times)
        
        logger.info(f"  Durchschnitt: {avg_time:.2f} ms, Median: {median_time:.2f} ms")
        logger.info(f"  Min: {min_time:.2f} ms, Max: {max_time:.2f} ms, Fehler: {errors}")
        
        result = {
            "average_ms": avg_time,
            "median_ms": median_time,
            "min_ms": min_time,
            "max_ms": max_time,
            "errors": errors,
            "samples": len(response_times),
            "url": url,
            "method": method,
            "db_stats": db_stats
        }
        
        # Überprüfe, ob wir Optimierungshinweise haben
        if db_stats and "query_count" in db_stats and db_stats["query_count"] > 10:
            result["optimization_hints"] = [
                f"Hohe Anzahl an Datenbankabfragen: {db_stats['query_count']}",
                "Implementiere Batch-Abfragen oder verringere die Anzahl der Abfragen"
            ]
            
        return result
    
    return None

def test_api_module(module_name, endpoints, iterations=10):
    """Testet alle Endpunkte eines API-Moduls"""
    results = []
    
    logger.info(f"Starte Performance-Tests für Modul: {module_name}")
    
    for endpoint in endpoints:
        method = endpoint["method"]
        path = endpoint["path"]
        name = endpoint["name"]
        
        url = f"{API_HOST}{path}"
        logger.info(f"Teste Endpunkt: {name} ({method} {path})")
        
        result = measure_response_time(method, url, iterations)
        if result:
            result["name"] = name
            result["module"] = module_name
            results.append(result)
    
    return results

def run_all_tests(modules=None, iterations=10, parallel=False):
    """Führt Tests für alle oder ausgewählte API-Module durch"""
    all_results = []
    
    if modules is None:
        modules = list(API_ENDPOINTS.keys())
    
    logger.info(f"Starte Performance-Tests für Module: {', '.join(modules)}")
    
    # Wähle zwischen paralleler und sequentieller Ausführung
    if parallel:
        with ThreadPoolExecutor(max_workers=min(len(modules), 5)) as executor:
            futures = {}
            for module in modules:
                if module in API_ENDPOINTS:
                    future = executor.submit(
                        test_api_module, 
                        module, 
                        API_ENDPOINTS[module],
                        iterations
                    )
                    futures[future] = module
            
            for future in futures:
                module = futures[future]
                try:
                    results = future.result()
                    all_results.extend(results)
                except Exception as e:
                    logger.error(f"Fehler bei Modul {module}: {str(e)}")
    else:
        for module in modules:
            if module in API_ENDPOINTS:
                results = test_api_module(module, API_ENDPOINTS[module], iterations)
                all_results.extend(results)
            else:
                logger.warning(f"Unbekanntes Modul: {module}")
    
    return all_results

def analyze_results(results):
    """Analysiert die Testergebnisse und identifiziert Engpässe"""
    if not results:
        logger.warning("Keine Ergebnisse zur Analyse vorhanden")
        return {}
    
    # Gruppiere Ergebnisse nach Modul
    modules = {}
    for result in results:
        module = result["module"]
        if module not in modules:
            modules[module] = []
        modules[module].append(result)
    
    analysis = {
        "summary": {
            "total_endpoints": len(results),
            "modules_tested": len(modules),
            "slowest_endpoints": [],
            "fastest_endpoints": [],
            "most_variable": [],
            "database_intensive": []  # Neue Kategorie für DB-intensive Endpunkte
        },
        "modules": {},
        "database_recommendations": []  # Neue Kategorie für DB-Optimierungsempfehlungen
    }
    
    # Sortiere Endpunkte nach Durchschnittszeit
    sorted_by_avg = sorted(results, key=lambda x: x["average_ms"], reverse=True)
    
    # Identifiziere die langsamsten Endpunkte
    slowest = sorted_by_avg[:min(5, len(sorted_by_avg))]
    analysis["summary"]["slowest_endpoints"] = [
        {
            "name": endpoint["name"],
            "module": endpoint["module"],
            "method": endpoint["method"],
            "url": endpoint["url"],
            "average_ms": endpoint["average_ms"]
        }
        for endpoint in slowest
    ]
    
    # Identifiziere die schnellsten Endpunkte
    fastest = sorted_by_avg[-min(5, len(sorted_by_avg)):]
    analysis["summary"]["fastest_endpoints"] = [
        {
            "name": endpoint["name"],
            "module": endpoint["module"],
            "method": endpoint["method"],
            "url": endpoint["url"],
            "average_ms": endpoint["average_ms"]
        }
        for endpoint in reversed(fastest)
    ]
    
    # Berechne Variabilität (Max - Min) / Median
    for result in results:
        result["variability"] = (result["max_ms"] - result["min_ms"]) / result["median_ms"] if result["median_ms"] > 0 else 0
    
    # Identifiziere Endpunkte mit der höchsten Variabilität
    sorted_by_var = sorted(results, key=lambda x: x["variability"], reverse=True)
    most_variable = sorted_by_var[:min(5, len(sorted_by_var))]
    analysis["summary"]["most_variable"] = [
        {
            "name": endpoint["name"],
            "module": endpoint["module"],
            "method": endpoint["method"],
            "url": endpoint["url"],
            "variability": endpoint["variability"],
            "min_ms": endpoint["min_ms"],
            "max_ms": endpoint["max_ms"]
        }
        for endpoint in most_variable
    ]
    
    # Identifiziere Endpunkte mit intensiver Datenbanknutzung
    db_intensive = []
    for result in results:
        if "db_stats" in result and result["db_stats"]:
            db_stats = result["db_stats"]
            if "query_count" in db_stats and db_stats["query_count"] > 5:
                db_intensive.append({
                    "name": result["name"],
                    "module": result["module"],
                    "method": result["method"],
                    "url": result["url"],
                    "query_count": db_stats["query_count"],
                    "average_query_time": db_stats.get("average_query_time", 0),
                    "slowest_query": db_stats.get("slowest_query", ""),
                    "slowest_query_time": db_stats.get("slowest_query_time", 0)
                })
    
    # Sortiere nach Anzahl der Abfragen
    db_intensive = sorted(db_intensive, key=lambda x: x["query_count"], reverse=True)
    analysis["summary"]["database_intensive"] = db_intensive[:min(5, len(db_intensive))]
    
    # Modulspezifische Analysen
    for module_name, module_results in modules.items():
        module_avg = statistics.mean([r["average_ms"] for r in module_results])
        slowest_in_module = sorted(module_results, key=lambda x: x["average_ms"], reverse=True)[0]
        
        analysis["modules"][module_name] = {
            "endpoint_count": len(module_results),
            "average_response_time": module_avg,
            "slowest_endpoint": {
                "name": slowest_in_module["name"],
                "method": slowest_in_module["method"],
                "url": slowest_in_module["url"],
                "average_ms": slowest_in_module["average_ms"]
            }
        }
        
        # Füge DB-Optimierungsempfehlungen hinzu
        if any("db_stats" in r and r["db_stats"] for r in module_results):
            db_heavy_endpoints = []
            for r in module_results:
                if "db_stats" in r and r["db_stats"] and "query_count" in r["db_stats"]:
                    if r["db_stats"]["query_count"] > 5:
                        db_heavy_endpoints.append({
                            "name": r["name"],
                            "url": r["url"],
                            "query_count": r["db_stats"]["query_count"]
                        })
            
            if db_heavy_endpoints:
                analysis["modules"][module_name]["database_heavy_endpoints"] = db_heavy_endpoints
                
                # Empfehlungen basierend auf den Endpunkten
                for ep in db_heavy_endpoints:
                    analysis["database_recommendations"].append({
                        "module": module_name,
                        "endpoint": ep["name"],
                        "recommendation": f"Optimiere {ep['name']} mit {ep['query_count']} Queries",
                        "possible_solutions": [
                            "Implementiere Eager Loading für verknüpfte Daten",
                            "Verwende Joins statt separater Abfragen",
                            "Füge Indizes für häufig abgefragte Felder hinzu",
                            "Implementiere Caching für langsame Abfragen"
                        ]
                    })
    
    return analysis

def main():
    """Hauptfunktion"""
    global API_HOST
    
    parser = argparse.ArgumentParser(description="Performance-Profiler für API-Module")
    parser.add_argument("--modules", nargs="+", help="Zu testende API-Module (kommagetrennt)")
    parser.add_argument("--all-apis", action="store_true", help="Alle API-Module testen")
    parser.add_argument("--iterations", type=int, default=10, help="Anzahl der Testwiederholungen pro Endpunkt")
    parser.add_argument("--parallel", action="store_true", help="Module parallel testen")
    parser.add_argument("--host", default=API_HOST, help=f"API-Host (Standard: {API_HOST})")
    parser.add_argument("--output", help="Ausgabedatei für die Ergebnisse (JSON)")
    parser.add_argument("--db-focus", action="store_true", help="Fokus auf Datenbankabfragen")
    
    args = parser.parse_args()
    
    # API-Host aktualisieren, wenn über Kommandozeile angegeben
    API_HOST = args.host
    
    # Bestimme zu testende Module
    modules = None
    if args.all_apis:
        modules = list(API_ENDPOINTS.keys())
    elif args.modules:
        modules = args.modules
    
    if not modules:
        parser.error("Bitte --modules oder --all-apis angeben")
    
    # Führe Tests durch
    logger.info(f"Performance-Profiler startet mit {args.iterations} Iterationen pro Endpunkt")
    results = run_all_tests(modules, args.iterations, args.parallel)
    
    # Analysiere Ergebnisse
    analysis = analyze_results(results)
    
    # Ergebnisse ausgeben
    if args.output:
        output_data = {
            "raw_results": results,
            "analysis": analysis,
            "timestamp": time.time(),
            "config": {
                "host": API_HOST,
                "iterations": args.iterations,
                "modules": modules,
                "parallel": args.parallel,
                "db_focus": args.db_focus
            }
        }
        
        with open(args.output, "w") as f:
            json.dump(output_data, f, indent=2)
        
        logger.info(f"Ergebnisse wurden in {args.output} gespeichert")
    
    # Ausgabe der Zusammenfassung
    print("\n=== PERFORMANCE-ANALYSE ===")
    print(f"Getestete Module: {len(analysis['modules'])}")
    print(f"Getestete Endpunkte: {analysis['summary']['total_endpoints']}")
    
    print("\nLangsamste Endpunkte:")
    for i, endpoint in enumerate(analysis["summary"]["slowest_endpoints"]):
        print(f"{i+1}. {endpoint['name']} ({endpoint['module']}): {endpoint['average_ms']:.2f} ms")
    
    print("\nEndpunkte mit höchster Variabilität:")
    for i, endpoint in enumerate(analysis["summary"]["most_variable"]):
        print(f"{i+1}. {endpoint['name']} ({endpoint['module']}): {endpoint['min_ms']:.2f} - {endpoint['max_ms']:.2f} ms")
    
    # Ausgabe der DB-intensiven Endpunkte
    if "database_intensive" in analysis["summary"] and analysis["summary"]["database_intensive"]:
        print("\nDatenbank-intensive Endpunkte:")
        for i, endpoint in enumerate(analysis["summary"]["database_intensive"]):
            print(f"{i+1}. {endpoint['name']} ({endpoint['module']}): {endpoint['query_count']} Abfragen")
    
    print("\n=== DATENBANK-OPTIMIERUNGSEMPFEHLUNGEN ===")
    if analysis.get("database_recommendations"):
        for i, rec in enumerate(analysis["database_recommendations"]):
            print(f"{i+1}. {rec['recommendation']} ({rec['module']})")
            for j, solution in enumerate(rec['possible_solutions']):
                print(f"   - {solution}")
    else:
        print("Keine spezifischen Datenbankoptimierungen identifiziert.")
    
    print("\n=== ALLGEMEINE EMPFEHLUNGEN ===")
    print("1. Datenbankabfragen für langsame Endpunkte analysieren")
    print("2. Indexe für häufig abgefragte Felder implementieren")
    print("3. Batch-Processing für große Datensätze einführen")
    print("4. Query-Optimierung für komplexe Abfragen durchführen")

if __name__ == "__main__":
    main() 