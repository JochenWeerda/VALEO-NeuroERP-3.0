"""
Finance Mission - Direkte Playwright-Exploration
Führt die Finance-Mission mit Playwright durch, da SSO-Login für browser-use problematisch ist.
"""

import asyncio
import os
import json
import datetime
from pathlib import Path
from playwright.async_api import async_playwright

BASE_URL = os.environ.get("NEUROERP_URL", "http://localhost:3000")
OUT_DIR = Path("evidence/screenshots")
HANDOFF_DIR = Path("swarm/handoffs")

# Stelle sicher, dass die Verzeichnisse existieren
OUT_DIR.mkdir(parents=True, exist_ok=True)
HANDOFF_DIR.mkdir(parents=True, exist_ok=True)

# Finance-spezifische Screenshots
FINANCE_DIR = OUT_DIR / "finance"
FINANCE_DIR.mkdir(parents=True, exist_ok=True)


async def take_screenshot(page, name: str, description: str = ""):
    """Screenshot aufnehmen und Metadaten speichern"""
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{timestamp}_{name}.png"
    filepath = FINANCE_DIR / filename
    
    await page.screenshot(path=str(filepath), full_page=True)
    
    return {
        "filename": filename,
        "filepath": str(filepath),
        "description": description,
        "timestamp": timestamp,
        "url": page.url
    }


async def explore_finance():
    """Exploriert das Finance-Modul"""
    findings = []
    screenshots = []
    
    async with async_playwright() as p:
        # Browser starten (headless=False für Sichtbarkeit, persist browser)
        browser = await p.chromium.launch(
            headless=False, 
            slow_mo=500,
            args=['--start-maximized']  # Browser maximiert starten
        )
        context = await browser.new_context(
            viewport={"width": 1920, "height": 1080},
            locale="de-DE",
            no_viewport=True  # Browser-Fenster nicht auf Viewport-Größe beschränken
        )
        page = await context.new_page()
        
        # Browser-Fenster bleibt offen
        print("\n" + "="*60)
        print("[INFO] Browser-Fenster wurde geoeffnet")
        print("[INFO] Login ist nicht aktiviert - starte direkt mit Exploration")
        print("="*60)
        
        try:
            # 1. Navigiere zur Startseite
            print("[*] Navigiere zu:", BASE_URL)
            await page.goto(BASE_URL, wait_until="networkidle")
            await asyncio.sleep(2)
            
            screenshot = await take_screenshot(page, "01_homepage", "Startseite / Login")
            screenshots.append(screenshot)
            print(f"  [OK] Screenshot: {screenshot['filename']}")
            
            # 2. Prüfe ob Login-Seite (aber Login ist nicht aktiviert)
            current_url = page.url
            page_title = await page.title()
            
            if "login" in current_url.lower() or "anmelden" in page_title.lower():
                print("  [INFO] Login-Seite erkannt, aber Login ist nicht aktiviert")
                print("  [INFO] Ueberspringe Login und navigiere direkt zum Dashboard...")
                # Versuche direkt zum Dashboard zu navigieren
                await page.goto(f"{BASE_URL}/dashboard", wait_until="networkidle")
                await asyncio.sleep(2)
            
            # 3. Warte auf Dashboard/Home
            print("\n[*] Warte auf Seite zu laden...")
            await asyncio.sleep(2)
            
            screenshot = await take_screenshot(page, "02_dashboard", "Dashboard nach Login")
            screenshots.append(screenshot)
            print(f"  [OK] Screenshot: {screenshot['filename']}")
            
            # 4. Navigiere zu Finance-Modul
            print("\n[*] Suche Finance-Modul...")
            
            # Versuche verschiedene Navigation-Methoden
            finance_selectors = [
                'a:has-text("Finance")',
                'a:has-text("Finanzen")',
                'a:has-text("FI")',
                '[href*="finance"]',
                '[href*="finanzen"]',
                'button:has-text("Finance")',
                'button:has-text("Finanzen")',
            ]
            
            finance_found = False
            for selector in finance_selectors:
                try:
                    element = page.locator(selector).first
                    if await element.is_visible(timeout=2000):
                        print(f"  [OK] Finance-Link gefunden: {selector}")
                        await element.click()
                        await asyncio.sleep(2)
                        finance_found = True
                        break
                except:
                    continue
            
            if not finance_found:
                print("  [WARN] Finance-Modul nicht gefunden - versuche direkte Navigation")
                await page.goto(f"{BASE_URL}/finance", wait_until="networkidle")
                await asyncio.sleep(2)
            
            screenshot = await take_screenshot(page, "03_finance_module", "Finance-Modul Übersicht")
            screenshots.append(screenshot)
            print(f"  [OK] Screenshot: {screenshot['filename']}")
            
            # 5. Suche Invoices/Rechnungen
            print("\n[*] Suche Invoices/Rechnungen...")
            
            invoice_selectors = [
                'a:has-text("Invoices")',
                'a:has-text("Rechnungen")',
                'a:has-text("Invoice")',
                'a:has-text("Rechnung")',
                '[href*="invoice"]',
                '[href*="rechnung"]',
            ]
            
            invoice_found = False
            for selector in invoice_selectors:
                try:
                    element = page.locator(selector).first
                    if await element.is_visible(timeout=2000):
                        print(f"  [OK] Invoice-Link gefunden: {selector}")
                        await element.click()
                        await asyncio.sleep(2)
                        invoice_found = True
                        break
                except:
                    continue
            
            if not invoice_found:
                print("  [WARN] Invoice-Link nicht gefunden - versuche direkte Navigation")
                await page.goto(f"{BASE_URL}/finance/invoices", wait_until="networkidle")
                await asyncio.sleep(2)
            
            screenshot = await take_screenshot(page, "04_invoices_list", "Invoices-Liste")
            screenshots.append(screenshot)
            print(f"  [OK] Screenshot: {screenshot['filename']}")
            
            # 6. Versuche neue Rechnung zu erstellen
            print("\n[*] Suche 'Neue Rechnung' Button...")
            
            create_selectors = [
                'button:has-text("New")',
                'button:has-text("Neu")',
                'button:has-text("Create")',
                'button:has-text("Erstellen")',
                'a:has-text("New Invoice")',
                'a:has-text("Neue Rechnung")',
                '[href*="new"]',
                '[href*="create"]',
            ]
            
            create_found = False
            for selector in create_selectors:
                try:
                    element = page.locator(selector).first
                    if await element.is_visible(timeout=2000):
                        print(f"  [OK] Create-Button gefunden: {selector}")
                        await element.click()
                        await asyncio.sleep(2)
                        create_found = True
                        break
                except:
                    continue
            
            if create_found:
                screenshot = await take_screenshot(page, "05_create_invoice_form", "Rechnung erstellen - Formular")
                screenshots.append(screenshot)
                print(f"  [OK] Screenshot: {screenshot['filename']}")
                
                # Analysiere Formular-Felder
                form_fields = await page.locator('input, select, textarea').all()
                field_info = []
                for field in form_fields[:10]:  # Erste 10 Felder
                    try:
                        label = await field.get_attribute("placeholder") or await field.get_attribute("name") or "Unbekannt"
                        field_type = await field.get_attribute("type") or "text"
                        field_info.append({"label": label, "type": field_type})
                    except:
                        pass
                
                findings.append({
                    "type": "form_analysis",
                    "fields_found": len(form_fields),
                    "sample_fields": field_info
                })
            else:
                print("  [WARN] Create-Button nicht gefunden")
                findings.append({
                    "type": "missing_feature",
                    "feature": "Create Invoice Button",
                    "severity": "high"
                })
            
            # 7. Weitere Finance-Bereiche explorieren
            print("\n[*] Exploriere weitere Finance-Bereiche...")
            
            # Versuche zu Payments zu navigieren
            payment_selectors = [
                'a:has-text("Payment")',
                'a:has-text("Zahlung")',
                '[href*="payment"]',
            ]
            
            for selector in payment_selectors:
                try:
                    element = page.locator(selector).first
                    if await element.is_visible(timeout=2000):
                        print(f"  [OK] Payment-Link gefunden: {selector}")
                        await element.click()
                        await asyncio.sleep(2)
                        screenshot = await take_screenshot(page, "06_payments", "Payments-Bereich")
                        screenshots.append(screenshot)
                        print(f"  [OK] Screenshot: {screenshot['filename']}")
                        break
                except:
                    continue
            
            # Zusammenfassung
            print("\n" + "="*60)
            print("[OK] Exploration abgeschlossen!")
            print(f"  Screenshots: {len(screenshots)}")
            print(f"  Findings: {len(findings)}")
            print("="*60)
            
        except Exception as e:
            print(f"\n[ERROR] Fehler waehrend Exploration: {e}")
            findings.append({
                "type": "error",
                "message": str(e),
                "url": page.url
            })
            raise
        
        finally:
            # Browser bleibt offen für manuelle Inspektion
            print("\n" + "="*60)
            print("[INFO] Mission abgeschlossen")
            print("[INFO] Browser bleibt noch 10 Sekunden offen für Inspektion")
            print("="*60)
            await asyncio.sleep(10)
            await browser.close()
            print("[OK] Browser geschlossen")
    
    # JSON Summary erstellen
    ts = datetime.datetime.utcnow().isoformat().replace(":", "-")
    summary = {
        "mission": "Finance Module Exploration",
        "timestamp": ts,
        "base_url": BASE_URL,
        "screenshots": screenshots,
        "findings": findings,
        "summary": {
            "screenshots_count": len(screenshots),
            "findings_count": len(findings),
            "explored_modules": ["Finance", "Invoices"],
            "status": "completed"
        }
    }
    
    summary_file = FINANCE_DIR / f"finance_mission_{ts}.json"
    with open(summary_file, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    
    # Handoff-Note erstellen
    handoff_file = HANDOFF_DIR / f"ui-explorer-finance-{ts}.md"
    with open(handoff_file, "w", encoding="utf-8") as f:
        f.write(f"""# UI Explorer Handoff - Finance Module

**Date:** {datetime.datetime.utcnow().isoformat()}
**Explored URL:** {BASE_URL}
**Status:** [OK] Complete

## Mission Summary

- **Module:** Finance
- **Flows Explored:**
  - Finance Module Navigation
  - Invoices List
  - Create Invoice (attempted)
  - Payments (attempted)

## Screenshots

Total: {len(screenshots)} screenshots

""")
        for i, ss in enumerate(screenshots, 1):
            f.write(f"{i}. **{ss['description']}**\n")
            f.write(f"   - File: `{ss['filename']}`\n")
            f.write(f"   - URL: {ss['url']}\n")
            f.write(f"   - Timestamp: {ss['timestamp']}\n\n")
        
        f.write(f"""## Findings

Total: {len(findings)} findings

""")
        for i, finding in enumerate(findings, 1):
            f.write(f"{i}. **{finding.get('type', 'unknown')}**\n")
            if finding.get('feature'):
                f.write(f"   - Feature: {finding['feature']}\n")
            if finding.get('severity'):
                f.write(f"   - Severity: {finding['severity']}\n")
            if finding.get('message'):
                f.write(f"   - Message: {finding['message']}\n")
            f.write("\n")
        
        f.write(f"""## Evidence

- JSON Summary: `{summary_file}`
- Screenshots Directory: `{FINANCE_DIR}/`
- All Screenshots: {', '.join([ss['filename'] for ss in screenshots])}

## Next Steps

- [ ] Test-Planner: Create test plan from this handoff
- [ ] GAP-Analyst: Map capabilities to ERP reference taxonomy
- [ ] Feature-Engineer: Address identified gaps
""")
    
    print(f"\n[OK] Summary: {summary_file}")
    print(f"[OK] Handoff: {handoff_file}")
    
    return summary, handoff_file


if __name__ == "__main__":
    print("="*60)
    print("Finance Mission - Starting...")
    print(f"Target: {BASE_URL}")
    print("="*60)
    
    asyncio.run(explore_finance())
    
    print("\n[OK] Mission Complete!")

