"""
UI Explorer Script für Valero NeuroERP
Nutzt browser-use für semantische Browser-Exploration
"""

import asyncio
import os
import json
import datetime
from pathlib import Path
from browser_use import Browser, sandbox, ChatBrowserUse
from browser_use.agent.service import Agent

BASE_URL = os.environ.get("NEUROERP_URL", "http://localhost:3000")
OUT_DIR = Path("evidence/screenshots")
HANDOFF_DIR = Path("swarm/handoffs")

***REMOVED*** Stelle sicher, dass die Verzeichnisse existieren
OUT_DIR.mkdir(parents=True, exist_ok=True)
HANDOFF_DIR.mkdir(parents=True, exist_ok=True)


@sandbox(persist=True)
async def explore(browser: Browser):
    """Exploriert das NeuroERP Frontend und sammelt Screenshots/Flows"""
    llm = ChatBrowserUse(model="gpt-4o-mini")  ***REMOVED*** Kann angepasst werden
    
    ***REMOVED*** Mission: Finance Module explorieren
    task = f"""
    Go to {BASE_URL}.
    Log in with test credentials from environment variables.
    Explore module: FINANCE -> Invoices -> Create Invoice.
    Take screenshots of each step.
    For each screen, write a short label and save JSON summary.
    Document any missing fields, unclear steps, or validation issues.
    """
    
    agent = Agent(task=task, browser=browser, llm=llm)
    result = await agent.run()

    ***REMOVED*** Timestamp für eindeutige Dateinamen
    ts = datetime.datetime.utcnow().isoformat().replace(":", "-")
    
    ***REMOVED*** JSON Summary speichern
    summary_file = OUT_DIR / f"finance_flow_{ts}.json"
    with open(summary_file, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    ***REMOVED*** Handoff-Note erstellen
    handoff_file = HANDOFF_DIR / f"ui-explorer-finance-{ts}.md"
    with open(handoff_file, "w", encoding="utf-8") as f:
        f.write(f"""***REMOVED*** UI Explorer Handoff - Finance Module

**Date:** {datetime.datetime.utcnow().isoformat()}
**Explored URL:** {BASE_URL}

***REMOVED******REMOVED*** Flow Summary
- Module: Finance
- Flow: Invoices -> Create Invoice
- Screenshot IDs: See {summary_file.name}

***REMOVED******REMOVED*** Findings
- [ ] Document any missing fields
- [ ] Document unclear steps
- [ ] Document validation issues
- [ ] Document any errors encountered

***REMOVED******REMOVED*** Evidence
- JSON Summary: `{summary_file}`
- Screenshots: `{OUT_DIR}/`

***REMOVED******REMOVED*** Next Steps
- Test-Planner: Create test plan from this handoff
- GAP-Analyst: Map capabilities to ERP reference taxonomy
""")
    
    print(f"✅ Exploration complete. Summary: {summary_file}")
    print(f"✅ Handoff note: {handoff_file}")


if __name__ == "__main__":
    asyncio.run(explore())

