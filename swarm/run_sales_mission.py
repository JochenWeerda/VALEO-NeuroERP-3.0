"""
Sales Mission - Direkte Playwright-Exploration
Führt die Sales-Mission mit Playwright durch, um Evidence für GAP-Analyse zu sammeln.
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

# Sales-spezifische Screenshots
SALES_DIR = OUT_DIR / "sales"
SALES_DIR.mkdir(parents=True, exist_ok=True)


async def take_screenshot(page, name: str, description: str = ""):
    """Screenshot aufnehmen und Metadaten speichern"""
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{timestamp}_{name}.png"
    filepath = SALES_DIR / filename
    
    await page.screenshot(path=str(filepath), full_page=True)
    
    return {
        "filename": filename,
        "filepath": str(filepath),
        "description": description,
        "timestamp": timestamp,
        "url": page.url
    }


async def explore_sales():
    """Exploriert das Sales-Modul"""
    findings = []
    screenshots = []
    flows = []
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=False, 
            slow_mo=500,
            args=['--start-maximized']
        )
        context = await browser.new_context(
            viewport={"width": 1920, "height": 1080},
            locale="de-DE",
            no_viewport=True
        )
        page = await context.new_page()
        
        print("\n" + "="*60)
        print("[INFO] Browser-Fenster wurde geoeffnet")
        print("[INFO] Starte Sales-Modul Exploration")
        print("="*60)
        
        try:
            # 1. Navigiere zur Startseite
            print("[*] Navigiere zu:", BASE_URL)
            await page.goto(BASE_URL, wait_until="networkidle")
            await asyncio.sleep(2)
            
            screenshot = await take_screenshot(page, "01_homepage", "Startseite / Login")
            screenshots.append(screenshot)
            print(f"  [OK] Screenshot: {screenshot['filename']}")
            
            # 2. Warte auf Dashboard/Home
            print("\n[*] Warte auf Seite zu laden...")
            await asyncio.sleep(2)
            
            screenshot = await take_screenshot(page, "02_dashboard", "Dashboard nach Login")
            screenshots.append(screenshot)
            print(f"  [OK] Screenshot: {screenshot['filename']}")
            
            # 3. Navigiere zu Sales-Modul
            print("\n[*] Suche Sales-Modul...")
            
            sales_selectors = [
                'a:has-text("Sales")',
                'a:has-text("Verkauf")',
                'a:has-text("SD")',
                '[href*="sales"]',
                '[href*="verkauf"]',
                'button:has-text("Sales")',
                'button:has-text("Verkauf")',
            ]
            
            sales_found = False
            for selector in sales_selectors:
                try:
                    element = page.locator(selector).first
                    if await element.is_visible(timeout=2000):
                        print(f"  [OK] Sales-Link gefunden: {selector}")
                        await element.click()
                        await asyncio.sleep(2)
                        sales_found = True
                        break
                except:
                    continue
            
            if not sales_found:
                print("  [WARN] Sales-Modul nicht gefunden - versuche direkte Navigation")
                await page.goto(f"{BASE_URL}/sales", wait_until="networkidle")
                await asyncio.sleep(2)
            
            screenshot = await take_screenshot(page, "03_sales_module", "Sales-Modul Übersicht")
            screenshots.append(screenshot)
            print(f"  [OK] Screenshot: {screenshot['filename']}")
            flows.append({"flow_id": "SALES-NAV-01", "description": "Sales Module Navigation"})
            
            # 4. FLOW 1: Offers/Angebote
            print("\n[*] FLOW 1: Exploriere Offers/Angebote...")
            
            offer_selectors = [
                'a:has-text("Offers")',
                'a:has-text("Angebote")',
                'a:has-text("Quote")',
                'a:has-text("Angebot")',
                '[href*="offer"]',
                '[href*="angebot"]',
                '[href*="quote"]',
            ]
            
            offer_found = False
            for selector in offer_selectors:
                try:
                    element = page.locator(selector).first
                    if await element.is_visible(timeout=2000):
                        print(f"  [OK] Offer-Link gefunden: {selector}")
                        await element.click()
                        await asyncio.sleep(2)
                        offer_found = True
                        break
                except:
                    continue
            
            if not offer_found:
                print("  [WARN] Offer-Link nicht gefunden - versuche direkte Navigation")
                await page.goto(f"{BASE_URL}/sales/offers", wait_until="networkidle")
                await asyncio.sleep(2)
            
            screenshot = await take_screenshot(page, "04_offers_list", "Offers-Liste")
            screenshots.append(screenshot)
            print(f"  [OK] Screenshot: {screenshot['filename']}")
            flows.append({"flow_id": "SALES-QTN-01", "description": "Offers List View"})
            
            # Versuche neues Angebot zu erstellen
            print("\n[*] Suche 'Neues Angebot' Button...")
            
            create_selectors = [
                'button:has-text("New")',
                'button:has-text("Neu")',
                'button:has-text("Create")',
                'button:has-text("Erstellen")',
                'a:has-text("New Offer")',
                'a:has-text("Neues Angebot")',
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
                screenshot = await take_screenshot(page, "05_create_offer_form", "Angebot erstellen - Formular")
                screenshots.append(screenshot)
                print(f"  [OK] Screenshot: {screenshot['filename']}")
                flows.append({"flow_id": "SALES-QTN-02", "description": "Create Offer Form"})
                
                # Analysiere Formular-Felder
                form_fields = await page.locator('input, select, textarea').all()
                field_info = []
                for field in form_fields[:15]:
                    try:
                        label = await field.get_attribute("placeholder") or await field.get_attribute("name") or "Unbekannt"
                        field_type = await field.get_attribute("type") or "text"
                        field_info.append({"label": label, "type": field_type})
                    except:
                        pass
                
                findings.append({
                    "type": "form_analysis",
                    "capability": "SALES-QTN-01",
                    "fields_found": len(form_fields),
                    "sample_fields": field_info
                })
            else:
                print("  [WARN] Create-Button nicht gefunden")
                findings.append({
                    "type": "missing_feature",
                    "capability": "SALES-QTN-01",
                    "feature": "Create Offer Button",
                    "severity": "high"
                })
            
            # 5. FLOW 2: Orders/Aufträge
            print("\n[*] FLOW 2: Exploriere Orders/Aufträge...")
            
            # Zurück zur Sales-Übersicht
            await page.goto(f"{BASE_URL}/sales", wait_until="networkidle")
            await asyncio.sleep(2)
            
            order_selectors = [
                'a:has-text("Orders")',
                'a:has-text("Aufträge")',
                'a:has-text("Order")',
                'a:has-text("Auftrag")',
                '[href*="order"]',
                '[href*="auftrag"]',
            ]
            
            order_found = False
            for selector in order_selectors:
                try:
                    element = page.locator(selector).first
                    if await element.is_visible(timeout=2000):
                        print(f"  [OK] Order-Link gefunden: {selector}")
                        await element.click()
                        await asyncio.sleep(2)
                        order_found = True
                        break
                except:
                    continue
            
            if not order_found:
                print("  [WARN] Order-Link nicht gefunden - versuche direkte Navigation")
                await page.goto(f"{BASE_URL}/sales/orders", wait_until="networkidle")
                await asyncio.sleep(2)
            
            screenshot = await take_screenshot(page, "06_orders_list", "Orders-Liste")
            screenshots.append(screenshot)
            print(f"  [OK] Screenshot: {screenshot['filename']}")
            flows.append({"flow_id": "SALES-ORD-01", "description": "Orders List View"})
            
            # Versuche neuen Auftrag zu erstellen
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
                screenshot = await take_screenshot(page, "07_create_order_form", "Auftrag erstellen - Formular")
                screenshots.append(screenshot)
                print(f"  [OK] Screenshot: {screenshot['filename']}")
                flows.append({"flow_id": "SALES-ORD-02", "description": "Create Order Form"})
            else:
                findings.append({
                    "type": "missing_feature",
                    "capability": "SALES-ORD-01",
                    "feature": "Create Order Button",
                    "severity": "high"
                })
            
            # 6. FLOW 3: Deliveries/Lieferungen
            print("\n[*] FLOW 3: Exploriere Deliveries/Lieferungen...")
            
            await page.goto(f"{BASE_URL}/sales", wait_until="networkidle")
            await asyncio.sleep(2)
            
            delivery_selectors = [
                'a:has-text("Deliveries")',
                'a:has-text("Lieferungen")',
                'a:has-text("Delivery")',
                'a:has-text("Lieferung")',
                '[href*="delivery"]',
                '[href*="lieferung"]',
            ]
            
            delivery_found = False
            for selector in delivery_selectors:
                try:
                    element = page.locator(selector).first
                    if await element.is_visible(timeout=2000):
                        print(f"  [OK] Delivery-Link gefunden: {selector}")
                        await element.click()
                        await asyncio.sleep(2)
                        delivery_found = True
                        break
                except:
                    continue
            
            if not delivery_found:
                print("  [WARN] Delivery-Link nicht gefunden - versuche direkte Navigation")
                await page.goto(f"{BASE_URL}/sales/deliveries", wait_until="networkidle")
                await asyncio.sleep(2)
            
            screenshot = await take_screenshot(page, "08_deliveries_list", "Deliveries-Liste")
            screenshots.append(screenshot)
            print(f"  [OK] Screenshot: {screenshot['filename']}")
            flows.append({"flow_id": "SALES-DLV-01", "description": "Deliveries List View"})
            
            # 7. FLOW 4: Invoices/Rechnungen
            print("\n[*] FLOW 4: Exploriere Invoices/Rechnungen...")
            
            await page.goto(f"{BASE_URL}/sales", wait_until="networkidle")
            await asyncio.sleep(2)
            
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
                await page.goto(f"{BASE_URL}/sales/invoices", wait_until="networkidle")
                await asyncio.sleep(2)
            
            screenshot = await take_screenshot(page, "09_invoices_list", "Invoices-Liste")
            screenshots.append(screenshot)
            print(f"  [OK] Screenshot: {screenshot['filename']}")
            flows.append({"flow_id": "SALES-BIL-01", "description": "Invoices List View"})
            
            # Zusammenfassung
            print("\n" + "="*60)
            print("[OK] Exploration abgeschlossen!")
            print(f"  Screenshots: {len(screenshots)}")
            print(f"  Findings: {len(findings)}")
            print(f"  Flows: {len(flows)}")
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
        "mission": "Sales Module Exploration",
        "timestamp": ts,
        "base_url": BASE_URL,
        "screenshots": screenshots,
        "flows": flows,
        "findings": findings,
        "summary": {
            "screenshots_count": len(screenshots),
            "findings_count": len(findings),
            "flows_count": len(flows),
            "explored_modules": ["Sales", "Offers", "Orders", "Deliveries", "Invoices"],
            "capabilities_touched": list(set([f.get("capability") for f in findings if f.get("capability")])),
            "status": "completed"
        }
    }
    
    summary_file = SALES_DIR / f"sales_mission_{ts}.json"
    with open(summary_file, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    
    # Handoff-Note erstellen
    handoff_file = HANDOFF_DIR / f"ui-explorer-sales-{ts}.md"
    with open(handoff_file, "w", encoding="utf-8") as f:
        f.write(f"""# UI Explorer Handoff - Sales Module

**Date:** {datetime.datetime.utcnow().isoformat()}
**Explored URL:** {BASE_URL}
**Status:** [OK] Complete

## Mission Summary

- **Module:** Sales / Order-to-Cash
- **Flows Explored:**
  - Sales Module Navigation (SALES-NAV-01)
  - Offers List & Create (SALES-QTN-01, SALES-QTN-02)
  - Orders List & Create (SALES-ORD-01, SALES-ORD-02)
  - Deliveries List (SALES-DLV-01)
  - Invoices List (SALES-BIL-01)

## Screenshots

Total: {len(screenshots)} screenshots

""")
        for i, ss in enumerate(screenshots, 1):
            f.write(f"{i}. **{ss['description']}**\n")
            f.write(f"   - File: `{ss['filename']}`\n")
            f.write(f"   - URL: {ss['url']}\n")
            f.write(f"   - Timestamp: {ss['timestamp']}\n\n")
        
        f.write(f"""## Flows

Total: {len(flows)} flows

""")
        for i, flow in enumerate(flows, 1):
            f.write(f"{i}. **{flow['flow_id']}** - {flow['description']}\n")
        
        f.write(f"""
## Findings

Total: {len(findings)} findings

""")
        for i, finding in enumerate(findings, 1):
            f.write(f"{i}. **{finding.get('type', 'unknown')}**\n")
            if finding.get('capability'):
                f.write(f"   - Capability: {finding['capability']}\n")
            if finding.get('feature'):
                f.write(f"   - Feature: {finding['feature']}\n")
            if finding.get('severity'):
                f.write(f"   - Severity: {finding['severity']}\n")
            if finding.get('message'):
                f.write(f"   - Message: {finding['message']}\n")
            f.write("\n")
        
        f.write(f"""## Evidence

- JSON Summary: `{summary_file}`
- Screenshots Directory: `{SALES_DIR}/`
- All Screenshots: {', '.join([ss['filename'] for ss in screenshots])}

## Capabilities Mapped

""")
        capabilities = list(set([f.get("capability") for f in findings if f.get("capability")]))
        for cap in capabilities:
            f.write(f"- {cap}\n")
        
        f.write(f"""
## Next Steps

- [ ] GAP-Analyst: Update matrix-sales.csv with evidence IDs
- [ ] Test-Planner: Create test plan from this handoff
- [ ] Feature-Engineer: Address identified gaps
- [ ] Run `python swarm/make_gaps_sales.py` to regenerate gaps-sales.md
""")
    
    print(f"\n[OK] Summary: {summary_file}")
    print(f"[OK] Handoff: {handoff_file}")
    
    return summary, handoff_file


if __name__ == "__main__":
    print("="*60)
    print("Sales Mission - Starting...")
    print(f"Target: {BASE_URL}")
    print("="*60)
    
    asyncio.run(explore_sales())
    
    print("\n[OK] Mission Complete!")

