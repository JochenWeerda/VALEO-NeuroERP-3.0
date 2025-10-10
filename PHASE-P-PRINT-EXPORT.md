***REMOVED*** 🖨️ PHASE P - DOKUMENTEN-DRUCK & NUMMERNKREISE

***REMOVED******REMOVED*** 🎯 Ziel

Automatische Generierung und Ausgabe von ERP-Belegen (Angebot, Auftrag, Lieferschein, Rechnung) als PDF-/HTML-Drucklayouts, inklusive Nummernkreis-Logik, Vorlagenverwaltung, Versionierung, Archiv-Speicher und Export-API.

---

***REMOVED******REMOVED*** 📋 Kontext

**Projektumgebung:**
- Monorepo (pnpm + Vite + React + FastAPI + MCP)
- Vorherige Phasen (K → O): Auth, Policies, Audit, SSE, FormBuilder + Belegfluss vollständig integriert
- Schemas für sales, delivery, invoice, purchase liegen vor

---

***REMOVED******REMOVED*** 🧩 Implementierungsplan

***REMOVED******REMOVED******REMOVED*** **1️⃣ Nummernkreis-Service (Backend)**

**Datei:** `app/services/numbering_service.py`

```python
"""
Numbering Service
Automatische Belegnummern-Generierung mit Nummernkreisen
"""

from __future__ import annotations
from typing import Dict
import sqlite3
from pathlib import Path


class NumberSeries:
    """Nummernkreis für eine Belegart"""
    
    def __init__(self, prefix: str, start: int = 1):
        self.prefix = prefix
        self.counter = start
    
    def next(self) -> str:
        """Generiert nächste Nummer"""
        num = f"{self.prefix}{self.counter:05d}"
        self.counter += 1
        return num
    
    def current(self) -> str:
        """Gibt aktuelle Nummer zurück (ohne Increment)"""
        return f"{self.prefix}{self.counter:05d}"


class NumberingStore:
    """SQLite-basierte Persistenz für Nummernkreise"""
    
    def __init__(self, db_path: str = "data/numbering.db"):
        self.db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
    
    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS number_series (
                    domain TEXT PRIMARY KEY,
                    prefix TEXT NOT NULL,
                    counter INTEGER NOT NULL DEFAULT 1
                )
            """)
            conn.commit()
    
    def get_next(self, domain: str, prefix: str) -> str:
        """Holt nächste Nummer und incrementiert Counter"""
        with sqlite3.connect(self.db_path) as conn:
            ***REMOVED*** Hole aktuellen Counter
            row = conn.execute(
                "SELECT counter FROM number_series WHERE domain = ?",
                (domain,)
            ).fetchone()
            
            if not row:
                ***REMOVED*** Erstelle neuen Nummernkreis
                conn.execute(
                    "INSERT INTO number_series (domain, prefix, counter) VALUES (?, ?, ?)",
                    (domain, prefix, 1)
                )
                counter = 1
            else:
                counter = row[0]
            
            ***REMOVED*** Generiere Nummer
            number = f"{prefix}{counter:05d}"
            
            ***REMOVED*** Incrementiere Counter
            conn.execute(
                "UPDATE number_series SET counter = counter + 1 WHERE domain = ?",
                (domain,)
            )
            conn.commit()
            
            return number


***REMOVED*** Global Store Instance
store = NumberingStore()


***REMOVED*** Vordefinierte Nummernkreise
SERIES_CONFIG = {
    "sales_order": "SO-",
    "sales_delivery": "DL-",
    "sales_invoice": "INV-",
    "purchase_order": "PO-",
    "goods_receipt": "GR-",
    "supplier_invoice": "PINV-",
    "weighing_ticket": "WT-",
}


def next_number(domain: str) -> str:
    """Generiert nächste Belegnummer für Domain"""
    prefix = SERIES_CONFIG.get(domain, f"{domain.upper()}-")
    return store.get_next(domain, prefix)
```

**Integration in `app/documents/router.py`:**
```python
from app.services.numbering_service import next_number

@router.post("/sales_order")
async def upsert_sales_order(doc: SalesOrder):
    ***REMOVED*** Auto-Nummer falls nicht vorhanden
    if not doc.number or doc.number == "":
        doc.number = next_number("sales_order")
    
    _DB[doc.number] = doc.model_dump()
    return {"ok": True, "number": doc.number}
```

---

***REMOVED******REMOVED******REMOVED*** **2️⃣ PDF-Generator (Backend)**

**Install:**
```bash
pip install reportlab
```

**Datei:** `app/services/pdf_service.py`

```python
"""
PDF Service
Generiert PDF-Dokumente aus Belegen
"""

from __future__ import annotations
from typing import Dict, Any, List
from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Table,
    TableStyle,
    Spacer,
    Image,
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_RIGHT, TA_CENTER
import logging

logger = logging.getLogger(__name__)


class PDFGenerator:
    """PDF-Generator für ERP-Belege"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Erstellt custom Styles"""
        self.styles.add(ParagraphStyle(
            name='RightAlign',
            parent=self.styles['Normal'],
            alignment=TA_RIGHT
        ))
        self.styles.add(ParagraphStyle(
            name='Header',
            parent=self.styles['Heading1'],
            fontSize=18,
            textColor=colors.HexColor('***REMOVED***1e40af')
        ))
    
    def render_document(
        self,
        doc_type: str,
        payload: Dict[str, Any],
        output_path: str
    ) -> str:
        """
        Rendert Beleg als PDF
        
        Args:
            doc_type: Belegtyp (z.B. "sales_order")
            payload: Beleg-Daten
            output_path: Ziel-Pfad für PDF
        
        Returns:
            Pfad zur erstellten PDF-Datei
        """
        doc = SimpleDocTemplate(output_path, pagesize=A4)
        story = []
        
        ***REMOVED*** Header
        title_map = {
            "sales_order": "Verkaufsauftrag",
            "sales_delivery": "Lieferschein",
            "sales_invoice": "Rechnung",
        }
        title = title_map.get(doc_type, doc_type.upper())
        
        story.append(Paragraph(
            f"{title} Nr. {payload.get('number', 'N/A')}",
            self.styles['Header']
        ))
        story.append(Spacer(1, 12 * mm))
        
        ***REMOVED*** Beleg-Daten
        fields_to_show = ['date', 'customerId', 'deliveryAddress', 'paymentTerms', 'notes']
        for field in fields_to_show:
            value = payload.get(field)
            if value:
                story.append(Paragraph(
                    f"<b>{field}:</b> {value}",
                    self.styles['Normal']
                ))
        
        story.append(Spacer(1, 12 * mm))
        
        ***REMOVED*** Positionen-Tabelle
        lines = payload.get('lines', [])
        if lines:
            table_data = [['Artikel', 'Menge', 'Preis', 'Summe']]
            
            for line in lines:
                article = line.get('article', '')
                qty = line.get('qty', 0)
                price = line.get('price', 0)
                total = round(qty * price, 2)
                table_data.append([article, str(qty), f"{price:.2f} €", f"{total:.2f} €"])
            
            ***REMOVED*** Gesamtsumme
            grand_total = sum(l.get('qty', 0) * l.get('price', 0) for l in lines)
            table_data.append(['', '', 'Gesamt:', f"{grand_total:.2f} €"])
            
            table = Table(table_data, colWidths=[80*mm, 30*mm, 30*mm, 30*mm])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, -1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ]))
            story.append(table)
        
        ***REMOVED*** PDF bauen
        doc.build(story)
        logger.info(f"Generated PDF: {output_path}")
        return output_path


***REMOVED*** Global Generator Instance
generator = PDFGenerator()
```

**API-Endpoint in `app/documents/router.py`:**
```python
from fastapi.responses import FileResponse
from app.services.pdf_service import generator
import os

@router.get("/{domain}/{doc_id}/print")
async def print_document(domain: str, doc_id: str):
    """Generiert PDF für Beleg"""
    doc = _DB.get(doc_id)
    if not doc:
        raise HTTPException(404, "Document not found")
    
    ***REMOVED*** PDF generieren
    pdf_path = f"data/temp/{doc_id}.pdf"
    Path(pdf_path).parent.mkdir(parents=True, exist_ok=True)
    
    generator.render_document(domain, doc, pdf_path)
    
    return FileResponse(
        pdf_path,
        media_type="application/pdf",
        filename=f"{doc_id}.pdf"
    )
```

---

***REMOVED******REMOVED******REMOVED*** **3️⃣ Frontend - Druck & Export**

**Datei:** `packages/frontend-web/src/features/documents/PrintButton.tsx`

```typescript
import * as React from "react"
import { Button } from "@/components/ui/button"

type Props = {
  domain: string
  documentId: string
}

export function PrintButton({ domain, documentId }: Props): JSX.Element {
  function handlePrint(): void {
    window.open(
      `/api/mcp/documents/${domain}/${documentId}/print`,
      "_blank"
    )
  }

  return (
    <Button variant="secondary" onClick={handlePrint}>
      📄 PDF drucken
    </Button>
  )
}
```

**Integration in BelegFlowPanel:**
```typescript
<div className="flex gap-2">
  <PrintButton domain="sales_order" documentId={current.number} />
  {nextTypes.map((n) => (
    <Button key={n.to} variant="secondary" onClick={() => onCreateFollowUp(n.to)}>
      → {n.label}
    </Button>
  ))}
</div>
```

---

***REMOVED******REMOVED******REMOVED*** **4️⃣ Archivierung & Versionierung**

**Datei:** `app/services/archive_service.py`

```python
"""
Archive Service
Versionierte Archivierung von Belegen mit Integrität-Check
"""

from __future__ import annotations
import json
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List


class ArchiveService:
    """Archivierungs-Service für Belege"""
    
    def __init__(self, base_path: str = "data/archives"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
        self.index_file = self.base_path / "index.json"
        self._load_index()
    
    def _load_index(self):
        """Lädt Archiv-Index"""
        if self.index_file.exists():
            with open(self.index_file, 'r') as f:
                self.index = json.load(f)
        else:
            self.index = {}
    
    def _save_index(self):
        """Speichert Archiv-Index"""
        with open(self.index_file, 'w') as f:
            json.dump(self.index, f, indent=2)
    
    def archive(
        self,
        domain: str,
        doc_id: str,
        file_path: str,
        user: str
    ) -> Dict[str, Any]:
        """
        Archiviert Dokument mit Hash-Signatur
        
        Args:
            domain: Belegtyp (z.B. "sales_order")
            doc_id: Beleg-ID
            file_path: Pfad zur PDF-Datei
            user: User der archiviert hat
        
        Returns:
            Archive-Metadaten
        """
        ***REMOVED*** Hash berechnen
        with open(file_path, 'rb') as f:
            file_hash = hashlib.sha256(f.read()).hexdigest()
        
        ***REMOVED*** Archiv-Pfad
        year = datetime.now().year
        archive_dir = self.base_path / domain / str(year)
        archive_dir.mkdir(parents=True, exist_ok=True)
        
        ***REMOVED*** Datei kopieren
        archive_path = archive_dir / f"{doc_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        import shutil
        shutil.copy(file_path, archive_path)
        
        ***REMOVED*** Index aktualisieren
        if doc_id not in self.index:
            self.index[doc_id] = []
        
        entry = {
            "timestamp": datetime.now().isoformat(),
            "user": user,
            "path": str(archive_path),
            "hash": file_hash,
            "domain": domain,
        }
        self.index[doc_id].append(entry)
        self._save_index()
        
        return entry
    
    def get_history(self, doc_id: str) -> List[Dict[str, Any]]:
        """Holt Archiv-Historie für Beleg"""
        return self.index.get(doc_id, [])


***REMOVED*** Global Archive Instance
archive = ArchiveService()
```

**API-Endpoint:**
```python
from app.services.archive_service import archive

@router.get("/{domain}/{doc_id}/history")
async def get_document_history(domain: str, doc_id: str):
    """Holt Archiv-Historie"""
    history = archive.get_history(doc_id)
    return {"ok": True, "data": history}
```

---

***REMOVED******REMOVED******REMOVED*** **5️⃣ Export-API (CSV/XLSX)**

**Install:**
```bash
pip install pandas openpyxl
```

**Datei:** `app/services/export_service.py`

```python
"""
Export Service
Exportiert Belege als CSV/XLSX
"""

from __future__ import annotations
import pandas as pd
from typing import List, Dict, Any
from pathlib import Path


class ExportService:
    """Export-Service für Belege"""
    
    def export_to_csv(
        self,
        documents: List[Dict[str, Any]],
        output_path: str
    ) -> str:
        """Exportiert Belege als CSV"""
        ***REMOVED*** Flatten documents
        rows = []
        for doc in documents:
            row = {
                'number': doc.get('number'),
                'date': doc.get('date'),
                'customer': doc.get('customerId'),
                'total': sum(
                    l.get('qty', 0) * l.get('price', 0)
                    for l in doc.get('lines', [])
                ),
            }
            rows.append(row)
        
        df = pd.DataFrame(rows)
        df.to_csv(output_path, index=False)
        return output_path
    
    def export_to_xlsx(
        self,
        documents: List[Dict[str, Any]],
        output_path: str
    ) -> str:
        """Exportiert Belege als XLSX"""
        rows = []
        for doc in documents:
            row = {
                'Belegnummer': doc.get('number'),
                'Datum': doc.get('date'),
                'Kunde': doc.get('customerId'),
                'Gesamt': sum(
                    l.get('qty', 0) * l.get('price', 0)
                    for l in doc.get('lines', [])
                ),
            }
            rows.append(row)
        
        df = pd.DataFrame(rows)
        df.to_excel(output_path, index=False, engine='openpyxl')
        return output_path


***REMOVED*** Global Export Instance
exporter = ExportService()
```

**API-Endpoint:**
```python
from fastapi.responses import FileResponse
from app.services.export_service import exporter

@router.get("/export/{domain}")
async def export_documents(
    domain: str,
    from_date: str = "",
    to_date: str = "",
    fmt: str = "csv"
):
    """Exportiert Belege als CSV/XLSX"""
    ***REMOVED*** Filter documents
    docs = [d for d in _DB.values() if d.get('type') == domain]
    
    ***REMOVED*** TODO: Date filtering
    
    ***REMOVED*** Export
    output_path = f"data/temp/export_{domain}.{fmt}"
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    
    if fmt == "xlsx":
        exporter.export_to_xlsx(docs, output_path)
    else:
        exporter.export_to_csv(docs, output_path)
    
    return FileResponse(
        output_path,
        media_type=f"application/{fmt}",
        filename=f"{domain}_export.{fmt}"
    )
```

---

***REMOVED******REMOVED******REMOVED*** **6️⃣ Frontend - Export-Button**

**Datei:** `packages/frontend-web/src/features/documents/ExportButton.tsx`

```typescript
import * as React from "react"
import { Button } from "@/components/ui/button"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"

type Props = {
  domain: string
}

export function ExportButton({ domain }: Props): JSX.Element {
  function handleExport(format: "csv" | "xlsx"): void {
    window.open(
      `/api/mcp/documents/export/${domain}?fmt=${format}`,
      "_blank"
    )
  }

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="outline">📊 Export</Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent>
        <DropdownMenuItem onClick={() => handleExport("csv")}>
          CSV
        </DropdownMenuItem>
        <DropdownMenuItem onClick={() => handleExport("xlsx")}>
          Excel (XLSX)
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  )
}
```

---

***REMOVED******REMOVED*** 🧾 Bonus-Features (Optional)

***REMOVED******REMOVED******REMOVED*** **QR-Code auf PDF**
```python
from reportlab.graphics.barcode.qr import QrCodeWidget
from reportlab.graphics.shapes import Drawing

def add_qr_code(story, data: str):
    qr = QrCodeWidget(data)
    d = Drawing(50, 50)
    d.add(qr)
    story.append(d)
```

***REMOVED******REMOVED******REMOVED*** **Mehrsprachige Vorlagen**
```python
TEMPLATES = {
    "invoice_de": "Rechnung",
    "invoice_en": "Invoice",
    "invoice_fr": "Facture",
}

def get_template(doc_type: str, lang: str = "de"):
    return TEMPLATES.get(f"{doc_type}_{lang}", doc_type)
```

***REMOVED******REMOVED******REMOVED*** **Batch-Druck**
```python
@router.post("/batch-print")
async def batch_print(doc_ids: List[str]):
    """Druckt mehrere Belege in eine PDF"""
    ***REMOVED*** Merge PDFs
    from PyPDF2 import PdfMerger
    
    merger = PdfMerger()
    for doc_id in doc_ids:
        ***REMOVED*** Generate individual PDF
        ***REMOVED*** Add to merger
        pass
    
    output = "data/temp/batch.pdf"
    merger.write(output)
    return FileResponse(output)
```

---

***REMOVED******REMOVED*** ✅ Definition of Done

- [ ] **Nummernkreise** funktionieren für alle Belegarten
- [ ] **`/print`** liefert valide PDF (< 100 KB, korrektes Layout)
- [ ] **Archivierung** und History API aktiv
- [ ] **Frontend-Buttons** integriert (Print, Export)
- [ ] **Export** (CSV/XLSX) funktioniert
- [ ] **Keine Lint-Warnings**
- [ ] **Tests** (Vitest) green

---

***REMOVED******REMOVED*** 🚀 Setup Commands

```bash
***REMOVED*** Backend
pip install reportlab pandas openpyxl PyPDF2

***REMOVED*** Frontend
cd packages/frontend-web
***REMOVED*** Keine neuen Dependencies nötig

***REMOVED*** Test
python scripts/test_numbering.py
python scripts/test_pdf_generation.py
```

---

***REMOVED******REMOVED*** 📚 Nächste Phase (Q)

**Phase Q - Beleg-Workflow & Freigabestufen**
- Genehmigungs-UI
- Workflow-Engine
- Digitale Signaturen
- Status-Transitions

---

**Bereit für Implementation?** 🚀

