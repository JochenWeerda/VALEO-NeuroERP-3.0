#!/usr/bin/env python3
"""
Backend-Diagnose-Skript für VALEO-NeuroERP
Prüft alle Imports und Dependencies
"""

import sys
import traceback
from pathlib import Path

# Füge Projekt-Root zu sys.path hinzu
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def diagnose():
    print("=" * 80)
    print("VALEO-NeuroERP Backend Diagnose")
    print("=" * 80)
    
    # Test 1: Core Imports
    print("\n1. Testing Core Imports...")
    try:
        import fastapi
        print(f"   ✅ fastapi: {fastapi.__version__}")
    except ImportError as e:
        print(f"   ❌ fastapi: {e}")
        return False
    
    try:
        import uvicorn
        print(f"   ✅ uvicorn: {uvicorn.__version__}")
    except ImportError as e:
        print(f"   ❌ uvicorn: {e}")
        return False
    
    try:
        import sqlalchemy
        print(f"   ✅ sqlalchemy: {sqlalchemy.__version__}")
    except ImportError as e:
        print(f"   ❌ sqlalchemy: {e}")
        return False
    
    # Test 2: App Core
    print("\n2. Testing App Core Modules...")
    try:
        from app.core.config import settings
        print(f"   ✅ app.core.config: {settings}")
    except Exception as e:
        print(f"   ❌ app.core.config: {e}")
        traceback.print_exc()
        return False
    
    try:
        from app.core.database import create_tables
        print(f"   ✅ app.core.database: {create_tables}")
    except Exception as e:
        print(f"   ❌ app.core.database: {e}")
        traceback.print_exc()
        return False
    
    # Test 3: API Router
    print("\n3. Testing API Router...")
    try:
        from app.api.v1.api import api_router
        print(f"   ✅ app.api.v1.api: {len(api_router.routes)} routes")
    except Exception as e:
        print(f"   ❌ app.api.v1.api: {e}")
        traceback.print_exc()
        return False
    
    # Test 4: Optional AI/ML Imports
    print("\n4. Testing Optional AI/ML Modules...")
    try:
        import langgraph
        print(f"   ✅ langgraph: imported successfully")
    except ImportError as e:
        print(f"   ⚠️  langgraph: {e} (optional)")
    except Exception as e:
        print(f"   ⚠️  langgraph: {e} (optional)")
    
    try:
        import chromadb
        print(f"   ✅ chromadb: imported successfully")
    except ImportError as e:
        print(f"   ⚠️  chromadb: {e} (optional)")
    except Exception as e:
        print(f"   ⚠️  chromadb: {e} (optional)")
    
    try:
        import nats
        print(f"   ✅ nats: imported successfully")
    except ImportError as e:
        print(f"   ⚠️  nats: {e} (optional)")
    except Exception as e:
        print(f"   ⚠️  nats: {e} (optional)")
    
    # Test 5: Main App
    print("\n5. Testing Main App Import...")
    try:
        from main import app
        print(f"   ✅ main.app: {app.title}")
        print(f"   ✅ Routes: {len(app.routes)}")
    except Exception as e:
        print(f"   ❌ main.app: {e}")
        traceback.print_exc()
        return False
    
    print("\n" + "=" * 80)
    print("✅ Diagnose ERFOLGREICH - Backend sollte startbar sein")
    print("=" * 80)
    return True

if __name__ == "__main__":
    success = diagnose()
    sys.exit(0 if success else 1)

