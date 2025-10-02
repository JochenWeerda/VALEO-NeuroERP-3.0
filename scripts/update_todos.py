import os
from datetime import datetime
from typing import List, Dict, Any
from pymongo import MongoClient
from query_documentation import DocumentationRetriever

def ensure_utf8(text: str) -> str:
    """Stellt sicher, dass ein Text UTF-8 kodiert ist."""
    if isinstance(text, bytes):
        return text.decode('utf-8', errors='replace')
    return text

def analyze_todo_priority(content: str) -> str:
    """Analysiert den Inhalt eines TODOs und bestimmt die Priorität."""
    high_priority_indicators = [
        "dringend", "kritisch", "wichtig", "sofort",
        "höchste priorität", "hohe priorität",
        "sicherheitsrelevant", "bug", "fehler",
        "blockiert", "blocker", "abhängigkeit"
    ]
    
    medium_priority_indicators = [
        "sollte", "wünschenswert", "verbesserung",
        "optimierung", "enhancement", "mittlere priorität"
    ]
    
    content_lower = content.lower()
    
    # Prüfe auf explizite Prioritätsmarkierungen
    if any(f"priorität: {p}" in content_lower for p in ["hoch", "high"]):
        return "Hoch"
    if any(f"priorität: {p}" in content_lower for p in ["mittel", "medium"]):
        return "Normal"
    if any(f"priorität: {p}" in content_lower for p in ["niedrig", "low"]):
        return "Normal"
    
    # Prüfe auf Prioritätsindikatoren
    if any(indicator in content_lower for indicator in high_priority_indicators):
        return "Hoch"
    if any(indicator in content_lower for indicator in medium_priority_indicators):
        return "Normal"
    
    return "Normal"

def normalize_path(path: str) -> str:
    """Normalisiert einen Dateipfad für den Vergleich."""
    # Entferne ./ und .\ am Anfang
    path = path.lstrip("./\\")
    # Ersetze Backslashes durch Forward Slashes
    path = path.replace("\\", "/")
    # Entferne #-Abschnitte
    path = path.split("#")[0]
    return path.lower().strip()

def is_duplicate_todo(todo: Dict[str, Any], todos: List[Dict[str, Any]]) -> bool:
    """Prüft, ob ein TODO bereits in der Liste existiert."""
    # Normalisiere den Text für den Vergleich
    todo_text = todo["todo_line"].lower().strip()
    todo_source = normalize_path(todo["source"])
    
    # Entferne häufige Präfixe und Markierungen
    for prefix in ["todo:", "todo", "fixme:", "fixme", "xxx:", "xxx", "- [ ]", "-", "**", "#"]:
        todo_text = todo_text.replace(prefix, "").strip()
    
    for existing in todos:
        existing_text = existing["todo_line"].lower().strip()
        existing_source = normalize_path(existing["source"])
        
        # Entferne die gleichen Präfixe
        for prefix in ["todo:", "todo", "fixme:", "fixme", "xxx:", "xxx", "- [ ]", "-", "**", "#"]:
            existing_text = existing_text.replace(prefix, "").strip()
        
        # Prüfe auf Textähnlichkeit
        if todo_text == existing_text:
            # Wenn die Quelle die gleiche ist oder eine die andere enthält
            if (todo_source == existing_source or
                todo_source in existing_source or
                existing_source in todo_source):
                return True
    
    return False

def extract_todo_context(lines: List[str], todo_index: int, window: int = 5) -> Dict[str, str]:
    """Extrahiert den Kontext eines TODOs mit verbesserter Analyse."""
    start = max(0, todo_index - window)
    end = min(len(lines), todo_index + window + 1)
    
    # Extrahiere Kontext
    context_before = "\n".join(lines[start:todo_index]).strip()
    todo_line = lines[todo_index].strip()
    context_after = "\n".join(lines[todo_index + 1:end]).strip()
    
    # Analysiere Titel
    title = todo_line
    for prefix in ["TODO:", "ToDo:", "FIXME:", "XXX:", "- [ ]", "-", "**", "#"]:
        if title.startswith(prefix):
            title = title[len(prefix):].strip()
    
    # Wenn der Titel leer ist oder nur aus dem Marker besteht,
    # versuche einen besseren Titel aus dem Kontext zu extrahieren
    if not title or title.lower() in ["todo", "fixme", "xxx"]:
        # Suche im nachfolgenden Kontext nach einem aussagekräftigen Titel
        next_lines = [l.strip() for l in lines[todo_index + 1:end]]
        for line in next_lines:
            if line and not line.startswith(("#", "//", "/*", "*", "*/", "'''", '"""', "-", "**")):
                title = line
                break
    
    # Entferne Markdown-Formatierung aus dem Titel
    title = title.strip("*#- ")
    
    # Stelle sicher, dass alle Strings UTF-8 kodiert sind
    return {
        "title": ensure_utf8(title),
        "context_before": ensure_utf8(context_before),
        "todo_line": ensure_utf8(todo_line),
        "context_after": ensure_utf8(context_after),
        "full_context": ensure_utf8(f"{context_before}\n{todo_line}\n{context_after}".strip())
    }

def get_todos_from_docs(retriever: DocumentationRetriever) -> List[Dict[str, Any]]:
    """Extrahiert TODOs aus der Dokumentation mit verbesserter Kontextanalyse."""
    todos = []
    
    # Direkte Textsuche nach TODO-Markierungen
    search_terms = [
        "TODO", "ToDo", "To-Do", "FIXME", "XXX",
        "Implementierung ausstehend", "Noch zu implementieren",
        "Muss implementiert werden", "Benötigt Implementierung",
        "Erweiterung geplant", "Zukünftige Erweiterung",
        "Implementiere", "Erweitere", "Verbessere"
    ]
    
    # Suche nach expliziten TODOs
    for term in search_terms:
        results = retriever.text_search(term)
        for doc in results:
            content = ensure_utf8(doc.get("content", ""))
            sections = doc.get("sections", [])
            
            # Suche in Hauptinhalt
            if content:
                lines = content.split("\n")
                for i, line in enumerate(lines):
                    if term.lower() in line.lower():
                        # Extrahiere TODO-Kontext
                        todo_context = extract_todo_context(lines, i)
                        
                        # Erstelle ein eindeutiges TODO-Item
                        todo_item = {
                            "type": "explicit",
                            "title": todo_context["title"],
                            "content": todo_context["full_context"],
                            "context_before": todo_context["context_before"],
                            "todo_line": todo_context["todo_line"],
                            "context_after": todo_context["context_after"],
                            "source": ensure_utf8(doc.get("file_path", doc.get("source", "Unbekannt"))),
                            "status": "Offen",
                            "priority": analyze_todo_priority(todo_context["full_context"]),
                            "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        }
                        
                        # Prüfe auf Duplikate mit verbesserter Erkennung
                        if not is_duplicate_todo(todo_item, todos):
                            todos.append(todo_item)
            
            # Suche in Abschnitten mit gleichem Verfahren
            for section in sections:
                section_content = ensure_utf8(section.get("content", ""))
                if section_content:
                    lines = section_content.split("\n")
                    for i, line in enumerate(lines):
                        if term.lower() in line.lower():
                            todo_context = extract_todo_context(lines, i)
                            
                            todo_item = {
                                "type": "explicit",
                                "title": todo_context["title"],
                                "content": todo_context["full_context"],
                                "context_before": todo_context["context_before"],
                                "todo_line": todo_context["todo_line"],
                                "context_after": todo_context["context_after"],
                                "source": ensure_utf8(f"{doc.get('file_path', doc.get('source', 'Unbekannt'))}#{section.get('title', '')}"),
                                "status": "Offen",
                                "priority": analyze_todo_priority(todo_context["full_context"]),
                                "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            }
                            
                            # Prüfe auf Duplikate mit verbesserter Erkennung
                            if not is_duplicate_todo(todo_item, todos):
                                todos.append(todo_item)
    
    # Semantische Suche nach impliziten TODOs
    semantic_queries = [
        "Aufgaben die noch implementiert werden müssen",
        "Geplante Erweiterungen und Verbesserungen",
        "Ausstehende Entwicklungsarbeiten",
        "Fehlende Funktionalitäten",
        "Bekannte Probleme die behoben werden müssen"
    ]
    
    for query in semantic_queries:
        results = retriever.semantic_search(query)
        for doc in results:
            content = ensure_utf8(doc.get("content", ""))
            
            # Prüfe auf relevante Schlüsselwörter
            keywords = [
                "implementier", "erweitern", "verbessern",
                "hinzufügen", "entwickeln", "beheben",
                "optimieren", "anpassen", "integrieren"
            ]
            
            if content and any(keyword in content.lower() for keyword in keywords):
                lines = content.split("\n")
                # Suche nach Zeilen mit Keywords
                for i, line in enumerate(lines):
                    if any(keyword in line.lower() for keyword in keywords):
                        todo_context = extract_todo_context(lines, i)
                        
                        todo_item = {
                            "type": "implicit",
                            "title": todo_context["title"],
                            "content": todo_context["full_context"],
                            "context_before": todo_context["context_before"],
                            "todo_line": todo_context["todo_line"],
                            "context_after": todo_context["context_after"],
                            "source": ensure_utf8(doc.get("file_path", doc.get("source", "Unbekannt"))),
                            "status": "Offen",
                            "priority": analyze_todo_priority(todo_context["full_context"]),
                            "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        }
                        
                        # Prüfe auf Duplikate mit verbesserter Erkennung
                        if not is_duplicate_todo(todo_item, todos):
                            todos.append(todo_item)
    
    return todos

def update_todo_file(todos: List[Dict[str, Any]]) -> None:
    """Aktualisiert die TODO.md Datei."""
    content = "# VALEO-NeuroERP Entwicklungs-TODOs\n\n"
    content += f"Automatisch aktualisiert durch RAG-System am {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
    
    # Gruppiere TODOs nach Typ und Priorität
    todo_groups = {
        "explicit": {"Hoch": [], "Normal": []},
        "implicit": {"Hoch": [], "Normal": []}
    }
    
    for todo in todos:
        todo_groups[todo["type"]][todo["priority"]].append(todo)
    
    # Explizite TODOs
    content += "## Explizit markierte TODOs\n\n"
    for priority in ["Hoch", "Normal"]:
        if todo_groups["explicit"][priority]:
            content += f"### {priority}e Priorität\n\n"
            for todo in todo_groups["explicit"][priority]:
                content += f"#### {todo['title']}\n\n"
                content += f"**Status:** {todo['status']}\n"
                content += f"**Quelle:** {todo['source']}\n"
                content += f"**Aktualisiert:** {todo['updated_at']}\n\n"
                if todo.get("context_before"):
                    content += "**Kontext davor:**\n```\n" + todo["context_before"] + "\n```\n\n"
                content += "**TODO:**\n```\n" + todo["todo_line"] + "\n```\n\n"
                if todo.get("context_after"):
                    content += "**Kontext danach:**\n```\n" + todo["context_after"] + "\n```\n\n"
    
    # Implizite TODOs
    content += "## Implizit erkannte TODOs\n\n"
    for priority in ["Hoch", "Normal"]:
        if todo_groups["implicit"][priority]:
            content += f"### {priority}e Priorität\n\n"
            for todo in todo_groups["implicit"][priority]:
                content += f"#### {todo['title']}\n\n"
                content += f"**Status:** {todo['status']}\n"
                content += f"**Quelle:** {todo['source']}\n"
                content += f"**Aktualisiert:** {todo['updated_at']}\n\n"
                if todo.get("context_before"):
                    content += "**Kontext davor:**\n```\n" + todo["context_before"] + "\n```\n\n"
                content += "**Relevanter Abschnitt:**\n```\n" + todo["todo_line"] + "\n```\n\n"
                if todo.get("context_after"):
                    content += "**Kontext danach:**\n```\n" + todo["context_after"] + "\n```\n\n"
    
    # Speichere die aktualisierte TODO-Liste mit expliziter UTF-8-Kodierung
    with open("memory-bank/todo.md", "w", encoding="utf-8") as f:
        f.write(content)

def main():
    # Setze den OpenAI API-Schlüssel
    with open("api_keys.local.json", "r") as f:
        import json
        api_keys = json.load(f)
        os.environ["OPENAI_API_KEY"] = api_keys["API_KEYS"]["OPENAI_API_KEY"]
    
    retriever = DocumentationRetriever()
    print("Starte TODO-Aktualisierung...")
    
    # Extrahiere TODOs aus der Dokumentation
    print("Extrahiere TODOs aus der Dokumentation...")
    todos = get_todos_from_docs(retriever)
    
    print(f"Gefunden: {len(todos)} TODOs")
    update_todo_file(todos)
    print("TODO-Liste erfolgreich aktualisiert!")

if __name__ == "__main__":
    main() 