import { useState } from 'react'
import { CopyCheck, Loader2, RefreshCw, Mail, Phone, MapPin, AlertTriangle } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { useDuplicates, type DuplicateGroup } from '@/lib/api/crm-duplicates'

/**
 * Kunden-Dubletten (DOM-CRM-004) — erkennt wahrscheinliche Doppelanlagen
 * (E-Mail/Telefon/Name+PLZ) und zeigt sie als Cluster zur Prüfung. Schließt den
 * Gap „Dublettenlogik". Zusammenführung folgt als eigener Slice.
 */

const REASON_LABEL: Record<string, string> = {
  email: 'E-Mail', telefon: 'Telefon', name_plz: 'Name + PLZ',
}
const REASON_ICON: Record<string, JSX.Element> = {
  email: <Mail size={12} />, telefon: <Phone size={12} />, name_plz: <MapPin size={12} />,
}

function GroupCard({ g }: { g: DuplicateGroup }) {
  return (
    <Card>
      <CardHeader className="py-3">
        <CardTitle className="text-sm flex flex-wrap items-center gap-2">
          <span>{g.anzahl} mögliche Dubletten</span>
          {g.konfidenz === 'hoch'
            ? <Badge variant="destructive">hohe Konfidenz</Badge>
            : <Badge variant="secondary">mittlere Konfidenz</Badge>}
          {g.gruende.map((r, i) => (
            <Badge key={i} variant="outline" className="gap-1">
              {REASON_ICON[r.typ]}{REASON_LABEL[r.typ] ?? r.typ}
            </Badge>
          ))}
        </CardTitle>
      </CardHeader>
      <CardContent className="p-0">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="text-xs text-muted-foreground border-b">
              <tr>
                <th className="text-left font-medium px-3 py-1.5">Kundennr.</th>
                <th className="text-left font-medium px-3 py-1.5">Name</th>
                <th className="text-left font-medium px-3 py-1.5">PLZ / Ort</th>
                <th className="text-left font-medium px-3 py-1.5">Telefon</th>
                <th className="text-left font-medium px-3 py-1.5">E-Mail</th>
              </tr>
            </thead>
            <tbody>
              {g.mitglieder.map((m) => (
                <tr key={m.kunden_nr} className="border-b last:border-0">
                  <td className="px-3 py-1.5 font-mono text-xs">{m.kunden_nr}</td>
                  <td className="px-3 py-1.5">{m.name1 || '—'}</td>
                  <td className="px-3 py-1.5">{[m.plz, m.ort].filter(Boolean).join(' ') || '—'}</td>
                  <td className="px-3 py-1.5">{m.tel || '—'}</td>
                  <td className="px-3 py-1.5">{m.email || '—'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <div className="px-3 py-2 text-xs text-muted-foreground border-t">
          Prüfen und ggf. zusammenführen (Zusammenführung folgt als eigener Slice).
        </div>
      </CardContent>
    </Card>
  )
}

export default function DublettenPage() {
  const [limit] = useState(100)
  const { data, isLoading, isFetching, refetch } = useDuplicates(limit)

  return (
    <div className="p-4 space-y-4">
      <div className="flex items-center gap-2">
        <CopyCheck size={20} className="text-primary" />
        <h1 className="text-lg font-semibold">Kunden-Dubletten</h1>
        {data && (
          <span className="text-sm text-muted-foreground">
            {data.total} Cluster · {data.geprueft} Kunden geprüft
          </span>
        )}
        <Button variant="outline" size="sm" className="ml-auto"
          onClick={() => void refetch()} disabled={isFetching}>
          {isFetching ? <Loader2 size={14} className="animate-spin" /> : <RefreshCw size={14} />}
          <span className="ml-1">Neu prüfen</span>
        </Button>
      </div>

      <p className="text-sm text-muted-foreground max-w-3xl">
        Wahrscheinliche Doppelanlagen, erkannt über gleiche E-Mail, Telefonnummer oder
        Name + PLZ (mit Namens-Normalisierung, z. B. umgestellte GbR-Namen).
      </p>

      {isLoading ? (
        <div className="flex items-center justify-center py-16 text-muted-foreground">
          <Loader2 className="animate-spin mr-2" size={18} /> Prüfe Kundenstamm …
        </div>
      ) : !data || data.groups.length === 0 ? (
        <Card><CardContent className="py-16 text-center text-sm text-muted-foreground">
          <AlertTriangle className="mx-auto mb-2 text-emerald-600" size={20} />
          Keine Dubletten gefunden.
        </CardContent></Card>
      ) : (
        <div className="space-y-3">
          {data.groups.map((g) => <GroupCard key={g.id} g={g} />)}
        </div>
      )}
    </div>
  )
}
