# KI Usability (Frontend)

Einheitliche Interaktion: **PageToolbar + Tastaturkürzel + Sprachsteuerung**. Alle Aktionen laufen über dieselbe Action-ID und den zentralen Dispatcher.

## Nutzung

- **VoiceButton** ist in der TopBar eingebunden (Feature-Flag `voiceControl`, Standard: an).
- **ActionDispatchProvider** umschließt das App-Layout in `DashboardLayout.tsx`.

## Handler in einer Maske registrieren

Damit Sprachbefehle wie „Speichern“ oder „Kundenauswahl“ in einer konkreten Maske ausgeführt werden, die Maske einen Handler registrieren:

```tsx
import { useActionDispatch } from '@/features/ki-usability'
import { useEffect } from 'react'

export default function OrderEditorPage() {
  const { registerHandler } = useActionDispatch()

  const handleSave = () => { /* ... */ }
  const handleOpenCustomerSelection = () => { /* Dialog öffnen */ }

  useEffect(() => {
    const unregisterSave = registerHandler('save-document', () => handleSave())
    const unregisterCustomer = registerHandler('open-customer-selection', () => handleOpenCustomerSelection())
    return () => {
      unregisterSave()
      unregisterCustomer()
    }
  }, [registerHandler, handleSave, handleOpenCustomerSelection])

  return (/* ... */)
}
```

Ohne Registrierung werden bekannte Aktionen trotzdem ausgeführt: **Navigation** (z. B. `nav-orders` → `/sales/auftraege-liste`) und **globale Shortcuts** (z. B. `save-document` → `globalShortcutManager.execute('save-document')`), sofern die Maske `useGlobalShortcuts` nutzt.

## API-URL

- Dev: Vite-Proxy `/api/ki-usability` → `http://localhost:5200` (ki-usability-api muss auf 5200 laufen).
- Optional: `VITE_KI_USABILITY_API_URL` setzen (z. B. `http://localhost:5200`).

## Feature-Flag

- `voiceControl`: An/Aus für den Mikrofon-Button in der TopBar (env: `VITE_FEATURE_VOICE_CONTROL`).
