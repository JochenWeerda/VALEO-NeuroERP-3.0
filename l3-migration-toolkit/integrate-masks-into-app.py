***REMOVED***!/usr/bin/env python3
"""
Integriert neue Masken in die App-Struktur
- Sidebar-Navigation
- Frontend-Routes
- Backend-Router
"""

import json
from pathlib import Path

print("=" * 80)
print("INTEGRATION: Masken in App-Struktur")
print("=" * 80)

***REMOVED*** Lade Kundenstamm-Schema
with open('mask-builder-framework/kundenstamm-complete-framework.json', 'r', encoding='utf-8') as f:
    kundenstamm_schema = json.load(f)

***REMOVED*** Lade Untertabellen-Mappings
with open('schemas/mappings/subtable-mappings.json', 'r', encoding='utf-8') as f:
    subtable_mappings = json.load(f)

print("\n📊 Schemas geladen:")
print(f"   Kundenstamm: {len(kundenstamm_schema['views'])} Views")
print(f"   Untertabellen: {len(subtable_mappings)} Tabellen")

***REMOVED*** Generiere Sidebar-Navigation Einträge
sidebar_items = []
for view in kundenstamm_schema['views']:
    view_id = view['id']
    view_label = view.get('label', view_id)
    
    ***REMOVED*** Icon basierend auf View-ID
    icon_map = {
        'overview': 'LayoutDashboard',
        'master': 'IdCard',
        'addresses': 'MapPinned',
        'contacts': 'Users',
        'billingTax': 'Receipt',
        'payment': 'CreditCard',
        'pricing': 'Tag',
        'delivery': 'Truck',
        'forms': 'FileText',
        'communication': 'MessagesSquare',
        'prefs': 'Settings2',
        'profiles': 'Building',
        'cooperative': 'Building2',
        'emailLists': 'Mail',
        'communities': 'Network',
        'cpd': 'Database',
        'discounts': 'Percent',
        'prices': 'Euro',
        'freetext': 'FileText',
        'extended': 'MoreVertical',
        'notes': 'StickyNote',
        'selections': 'Filter',
        'interfaces': 'Plug',
        'history': 'History'
    }
    
    icon = icon_map.get(view_id, 'FileText')
    
    sidebar_items.append({
        'id': view_id,
        'label': view_label,
        'icon': icon,
        'path': f"/verkauf/kunden-stamm/{view_id}"
    })

print(f"\n📋 Sidebar-Items generiert: {len(sidebar_items)}")

***REMOVED*** Generiere Backend-Routes
backend_routes = []
for view in kundenstamm_schema['views']:
    view_id = view['id']
    
    if 'subtable' in view:
        subtable_name = view['subtable']
        backend_routes.append({
            'path': f"/api/v1/{subtable_name}",
            'methods': ['GET', 'POST', 'PUT', 'DELETE'],
            'subtable': subtable_name
        })

print(f"\n🔗 Backend-Routes generiert: {len(backend_routes)}")

***REMOVED*** Speichere Integration-Config
integration_config = {
    'sidebar_items': sidebar_items,
    'backend_routes': backend_routes,
    'frontend_routes': [],
    'sql_tables': list(subtable_mappings.keys())
}

output_file = 'mask-builder-framework/integration-config.json'
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(integration_config, f, ensure_ascii=False, indent=2)

print(f"\n✅ Integration-Config gespeichert: {output_file}")

print("\n" + "=" * 80)
print("✅ INTEGRATION-KONFIGURATION ERSTELLT")
print("=" * 80)
print(f"\n📊 Statistiken:")
print(f"   Sidebar-Items: {len(sidebar_items)}")
print(f"   Backend-Routes: {len(backend_routes)}")
print(f"   SQL-Tabellen: {len(integration_config['sql_tables'])}")

