***REMOVED***!/usr/bin/env python3
***REMOVED*** -*- coding: utf-8 -*-

"""
Startskript für den GENXAIS-Prompt-Generator

Dieses Skript startet den GENXAIS-Prompt-Generator als Streamlit-App.
"""

import os
import sys
import subprocess
import time

def main():
    """Startet den GENXAIS-Prompt-Generator."""
    print("🧠 Starte GENXAIS-Prompt-Generator...")
    
    ***REMOVED*** Prüfe, ob Streamlit installiert ist
    try:
        import streamlit
        print("✅ Streamlit ist installiert.")
    except ImportError:
        print("❌ Streamlit ist nicht installiert. Installiere Streamlit...")
        subprocess.run([sys.executable, "-m", "pip", "install", "streamlit"], check=True)
        print("✅ Streamlit wurde installiert.")
    
    ***REMOVED*** Prüfe, ob die Generator-Datei existiert
    generator_path = os.path.join("scripts", "genxais_prompt_generator.py")
    if not os.path.exists(generator_path):
        print(f"❌ Generator-Datei nicht gefunden: {generator_path}")
        sys.exit(1)
    
    ***REMOVED*** Starte die Streamlit-App
    print("🚀 Starte Streamlit-App...")
    
    ***REMOVED*** Streamlit-Port konfigurieren
    port = 8501
    
    ***REMOVED*** Starte die App
    try:
        process = subprocess.Popen(
            [sys.executable, "-m", "streamlit", "run", generator_path, "--server.port", str(port)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        ***REMOVED*** Warte kurz, um zu sehen, ob die App startet
        time.sleep(2)
        
        if process.poll() is not None:
            ***REMOVED*** Prozess wurde beendet
            stdout, stderr = process.communicate()
            print(f"❌ Fehler beim Starten der App:\n{stderr}")
            sys.exit(1)
        
        ***REMOVED*** Öffne Browser
        import webbrowser
        webbrowser.open(f"http://localhost:{port}")
        
        print(f"✅ GENXAIS-Prompt-Generator läuft auf http://localhost:{port}")
        print("Drücke Strg+C, um die App zu beenden.")
        
        ***REMOVED*** Warte auf Benutzerabbruch
        process.wait()
    
    except KeyboardInterrupt:
        print("\n🛑 GENXAIS-Prompt-Generator wird beendet...")
        if 'process' in locals() and process.poll() is None:
            process.terminate()
            process.wait()
        print("✅ Beendet.")
    
    except Exception as e:
        print(f"❌ Fehler: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 