"""
Datenbankoptimierung für das ERP-System

Dieses Skript analysiert Datenbankabfragen im ERP-System und gibt Optimierungsvorschläge.
"""

import json
import time
import argparse
import requests
import logging
import sys
from typing import Dict, List, Any, Optional
from datetime import datetime
from tabulate import tabulate

# Logger konfigurieren
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("db_optimizer")

class QueryProfiler:
    """Klasse zur Profilierung von API-Endpunkten mit Fokus auf Datenbankabfragen"""
    
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.results = []
    
    def profile_endpoint(self, endpoint: str, method: str = "GET", params: Dict = None, iterations: int = 3) -> Dict:
        """Profiliert einen API-Endpunkt"""
        
        url = f"{self.base_url}{endpoint}"
        total_duration = 0
        query_counts = []
        query_times = []
        
        logger.info(f"Profiliere Endpunkt: {method} {endpoint}")
        
        for i in range(iterations):
            headers = {"x-profiling": "enabled"}
            
            start_time = time.time()
            
            if method == "GET":
                response = requests.get(url, params=params, headers=headers)
            elif method == "POST":
                response = requests.post(url, json=params, headers=headers)
            else:
                raise ValueError(f"Nicht unterstützte HTTP-Methode: {method}")
            
            end_time = time.time()
            
            # Gesamt-Antwortzeit
            duration = end_time - start_time
            total_duration += duration
            
            # Profiling-Daten aus Header extrahieren
            profiling_data = {}
            if "X-Profiling-Data" in response.headers:
                try:
                    profiling_data = json.loads(response.headers["X-Profiling-Data"])
                    query_counts.append(profiling_data.get("db_queries", 0))
                    query_times.append(profiling_data.get("db_time", 0))
                except json.JSONDecodeError:
                    logger.warning(f"Konnte Profiling-Daten nicht dekodieren: {response.headers.get('X-Profiling-Data')}")
            
            logger.debug(f"Iteration {i+1}/{iterations}: {duration:.3f}s, {profiling_data.get('db_queries', 'N/A')} Abfragen")
        
        # Ergebnisse berechnen
        avg_duration = total_duration / iterations
        avg_query_count = sum(query_counts) / len(query_counts) if query_counts else 0
        avg_query_time = sum(query_times) / len(query_times) if query_times else 0
        
        result = {
            "endpoint": endpoint,
            "method": method,
            "avg_duration": avg_duration,
            "avg_query_count": avg_query_count,
            "avg_query_time": avg_query_time,
            "query_time_percent": (avg_query_time / avg_duration) * 100 if avg_duration > 0 else 0,
            "iterations": iterations,
            "timestamp": datetime.now().isoformat()
        }
        
        self.results.append(result)
        return result
    
    def analyze_results(self) -> Dict:
        """Analysiert die Profiling-Ergebnisse und gibt Optimierungsvorschläge"""
        
        if not self.results:
            return {"message": "Keine Ergebnisse zur Analyse vorhanden"}
        
        # Nach Antwortzeit sortieren (absteigend)
        sorted_results = sorted(self.results, key=lambda r: r["avg_duration"], reverse=True)
        
        # Problematische Endpunkte identifizieren
        problematic_endpoints = []
        
        for result in sorted_results:
            issues = []
            
            # Zu viele Abfragen?
            if result["avg_query_count"] > 3:
                issues.append({
                    "type": "high_query_count",
                    "description": f"Hohe Anzahl von Datenbankabfragen ({result['avg_query_count']:.1f})",
                    "suggestion": "Abfragen zusammenfassen oder Batch-Verarbeitung verwenden"
                })
            
            # Hoher Anteil der Datenbankzeit an der Gesamtzeit?
            if result["query_time_percent"] > 70:
                issues.append({
                    "type": "high_db_time_ratio",
                    "description": f"Hoher Anteil an Datenbankzeit ({result['query_time_percent']:.1f}%)",
                    "suggestion": "Indexierung prüfen, Abfragen optimieren oder Caching einsetzen"
                })
            
            # Lange Antwortzeit?
            if result["avg_duration"] > 0.5:
                issues.append({
                    "type": "high_response_time",
                    "description": f"Lange Antwortzeit ({result['avg_duration']*1000:.0f}ms)",
                    "suggestion": "Gesamtoptimierung erforderlich, Caching, Indexierung und Code-Review"
                })
            
            if issues:
                problematic_endpoints.append({
                    "endpoint": result["endpoint"],
                    "method": result["method"],
                    "metrics": {
                        "avg_duration": result["avg_duration"],
                        "avg_query_count": result["avg_query_count"],
                        "avg_query_time": result["avg_query_time"],
                        "query_time_percent": result["query_time_percent"]
                    },
                    "issues": issues
                })
        
        # Gesamtanalyse
        total_avg_duration = sum(r["avg_duration"] for r in self.results) / len(self.results)
        total_avg_query_count = sum(r["avg_query_count"] for r in self.results) / len(self.results)
        
        return {
            "summary": {
                "endpoints_analyzed": len(self.results),
                "problematic_endpoints": len(problematic_endpoints),
                "avg_response_time": total_avg_duration,
                "avg_query_count": total_avg_query_count
            },
            "problematic_endpoints": problematic_endpoints,
            "timestamp": datetime.now().isoformat()
        }
    
    def print_results(self):
        """Gibt die Profiling-Ergebnisse in tabellarischer Form aus"""
        
        if not self.results:
            print("Keine Ergebnisse vorhanden")
            return
        
        table_data = []
        for r in sorted(self.results, key=lambda x: x["avg_duration"], reverse=True):
            table_data.append([
                r["endpoint"],
                r["method"],
                f"{r['avg_duration']*1000:.0f}ms",
                f"{r['avg_query_count']:.1f}",
                f"{r['avg_query_time']*1000:.0f}ms",
                f"{r['query_time_percent']:.1f}%"
            ])
        
        print("\nProfiling-Ergebnisse:")
        print(tabulate(
            table_data,
            headers=["Endpunkt", "Methode", "Dauer", "DB-Abfragen", "DB-Zeit", "DB-Zeit %"],
            tablefmt="pretty"
        ))
    
    def print_analysis(self, analysis: Dict):
        """Gibt die Analyse in lesbarer Form aus"""
        
        print("\n" + "="*80)
        print("DATENBANKOPTIMIERUNGS-ANALYSE")
        print("="*80)
        
        summary = analysis["summary"]
        print(f"\nZusammenfassung:")
        print(f"- {summary['endpoints_analyzed']} Endpunkte analysiert")
        print(f"- {summary['problematic_endpoints']} problematische Endpunkte gefunden")
        print(f"- Durchschnittliche Antwortzeit: {summary['avg_response_time']*1000:.0f}ms")
        print(f"- Durchschnittliche Anzahl DB-Abfragen: {summary['avg_query_count']:.1f}")
        
        if analysis["problematic_endpoints"]:
            print("\nProblematische Endpunkte:")
            
            for i, endpoint in enumerate(analysis["problematic_endpoints"], 1):
                print(f"\n{i}. {endpoint['method']} {endpoint['endpoint']}")
                print(f"   Antwortzeit: {endpoint['metrics']['avg_duration']*1000:.0f}ms")
                print(f"   DB-Abfragen: {endpoint['metrics']['avg_query_count']:.1f}")
                print(f"   DB-Zeit: {endpoint['metrics']['avg_query_time']*1000:.0f}ms ({endpoint['metrics']['query_time_percent']:.1f}%)")
                
                print("   Probleme:")
                for issue in endpoint["issues"]:
                    print(f"   - {issue['description']}")
                    print(f"     Vorschlag: {issue['suggestion']}")
        
        print("\n" + "="*80)

def main():
    """Hauptfunktion"""
    
    parser = argparse.ArgumentParser(description="Datenbankoptimierungstool für das ERP-System")
    parser.add_argument("--url", default="http://localhost:8000", help="Basis-URL des API-Servers")
    parser.add_argument("--endpoints", nargs="+", help="Zu profilierende Endpunkte")
    parser.add_argument("--iterations", type=int, default=3, help="Anzahl der Durchläufe pro Endpunkt")
    parser.add_argument("--output", help="Ausgabedatei für die Ergebnisse (JSON)")
    
    args = parser.parse_args()
    
    # Standard-Endpunkte, wenn keine angegeben wurden
    if not args.endpoints:
        args.endpoints = [
            "/api/v1/artikel",
            "/api/v1/artikel/1",
            "/api/v1/charge",
            "/api/v1/charge/1"
        ]
    
    # Profiler initialisieren
    profiler = QueryProfiler(args.url)
    
    # Endpunkte profilieren
    for endpoint in args.endpoints:
        profiler.profile_endpoint(endpoint, iterations=args.iterations)
    
    # Ergebnisse ausgeben
    profiler.print_results()
    
    # Ergebnisse analysieren
    analysis = profiler.analyze_results()
    profiler.print_analysis(analysis)
    
    # Ergebnisse in Datei speichern
    if args.output:
        with open(args.output, "w") as f:
            json.dump({
                "results": profiler.results,
                "analysis": analysis
            }, f, indent=2)
        
        logger.info(f"Ergebnisse in {args.output} gespeichert")

if __name__ == "__main__":
    main() 