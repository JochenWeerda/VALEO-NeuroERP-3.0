import asyncio
from pathlib import Path
from agents.pipeline_orchestrator import PipelineOrchestrator
from agents.task_handlers import (
    CircularDependencyResolver,
    CouplingReducer,
    ImportOptimizer,
    ServiceLayerImplementer
)

async def main():
    """Führt die Verbesserungs-Pipeline aus"""
    # Projektroot
    root = Path(__file__).parent.parent
    
    # Erstelle Orchestrator
    orchestrator = PipelineOrchestrator()
    
    # Initialisiere Pipeline
    await orchestrator.setup_pipeline()
    
    print("=== Starte Verbesserungs-Pipeline ===\n")
    
    # Phase 1: Analyse
    print("Phase 1: Analyse")
    orchestrator.current_phase = "ANALYZE"
    
    # Analysiere Abhängigkeiten
    resolver = CircularDependencyResolver(str(root))
    resolver.analyze_dependencies()
    cycles = resolver.cycles
    
    print(f"Gefundene Zyklen: {len(cycles)}")
    for cycle in cycles:
        print(f"  {' -> '.join(cycle)} -> {cycle[0]}")
        
    # Analysiere Kopplung
    reducer = CouplingReducer(str(root))
    reducer.analyze_coupling()
    
    print(f"\nModule mit hoher Kopplung: {len(reducer.high_coupling)}")
    for module in reducer.high_coupling:
        print(f"  {module}: {len(reducer.modules[module])} Abhängigkeiten")
        
    # Analysiere Imports
    optimizer = ImportOptimizer(str(root))
    optimizer.analyze_imports()
    
    # Phase 2: Implementierung
    print("\nPhase 2: Implementierung")
    orchestrator.current_phase = "IMPLEMENT"
    
    # Starte Pipeline
    await orchestrator.execute_pipeline()
    
    print("\n=== Pipeline abgeschlossen ===")
    
    # Zeige Ergebnisse
    completed = sum(1 for node in orchestrator.graph.nodes 
                   if orchestrator.graph.nodes[node]["status"] == "completed")
    failed = sum(1 for node in orchestrator.graph.nodes
                if orchestrator.graph.nodes[node]["status"] == "failed")
    
    print(f"\nErgebnisse:")
    print(f"  Abgeschlossene Tasks: {completed}")
    print(f"  Fehlgeschlagene Tasks: {failed}")
    
    # Speichere Handover-Dokumente
    print("\nHandover-Dokumente:")
    for task, handover in orchestrator.handovers.items():
        print(f"  {task}: {handover['timestamp']}")

if __name__ == "__main__":
    asyncio.run(main()) 