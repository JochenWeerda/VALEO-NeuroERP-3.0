/**
 * Datenqualitäts-Cockpit (Gap 040): Dubletten, Pflichtfelder, Referenzen.
 */

import { useState } from 'react'
import { useValidateDataQuality, useDataQualityEntityTypes } from '@/lib/api/admin'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { NativeSelect } from '@/components/ui/native-select'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import { AlertCircle, CheckCircle2, Database, Loader2, Play } from 'lucide-react'

const ENTITY_LABELS: Record<string, string> = {
  debtors: 'Debitoren',
  creditors: 'Kreditoren',
  articles: 'Artikel',
  business_partners: 'Geschäftspartner',
  harvest_acceptance: 'Ernte-Annahmen',
  agrar_settlements: 'Agrar-Abrechnungen',
  offene_posten: 'Offene Posten',
}

export default function DataQualityPage(): JSX.Element {
  const [selectedTypes, setSelectedTypes] = useState<string[] | undefined>(undefined)
  const { data: entityTypes = [] } = useDataQualityEntityTypes()
  const validateMutation = useValidateDataQuality()

  const handleValidate = () => {
    validateMutation.mutate(
      selectedTypes && selectedTypes.length > 0 ? selectedTypes : undefined
    )
  }

  const results = validateMutation.data ?? []
  const totalViolations = results.reduce((sum, r) => sum + r.total_count, 0)

  return (
    <div className="space-y-6 p-6">
      <div>
        <h1 className="flex items-center gap-2 text-2xl font-semibold">
          <Database className="h-6 w-6" />
          Datenqualität
        </h1>
        <p className="mt-1 text-muted-foreground">
          MDM-Regeln: Dubletten, Pflichtfelder und Referenzintegrität prüfen (Gap 040).
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Validierung ausführen</CardTitle>
          <CardDescription>
            Wählen Sie optional bestimmte Entity-Typen oder prüfen Sie alle.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex flex-wrap items-center gap-4">
            <div className="w-[220px]">
              <NativeSelect
                value={selectedTypes?.length === 1 ? selectedTypes[0] : 'all'}
                onValueChange={(value) => setSelectedTypes(value === 'all' ? undefined : [value])}
                options={[
                  { value: 'all', label: 'Alle Entity-Typen' },
                  ...(entityTypes ?? []).map((entityType) => ({
                    value: entityType,
                    label: ENTITY_LABELS[entityType] ?? entityType,
                  })),
                ]}
              />
            </div>
            <Button
              onClick={handleValidate}
              disabled={validateMutation.isPending}
            >
              {validateMutation.isPending ? (
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              ) : (
                <Play className="mr-2 h-4 w-4" />
              )}
              Prüfung starten
            </Button>
          </div>
        </CardContent>
      </Card>

      {validateMutation.isError && (
        <Card className="border-destructive">
          <CardContent className="pt-6">
            <p className="text-sm text-destructive">
              {validateMutation.error instanceof Error
                ? validateMutation.error.message
                : 'Validierung fehlgeschlagen'}
            </p>
          </CardContent>
        </Card>
      )}

      {results.length > 0 && (
        <>
          <div className="flex items-center gap-2">
            {totalViolations === 0 ? (
              <Badge variant="default" className="gap-1">
                <CheckCircle2 className="h-3 w-3" />
                Keine Verstöße
              </Badge>
            ) : (
              <Badge variant="destructive" className="gap-1">
                <AlertCircle className="h-3 w-3" />
                {totalViolations} Verstoß(verstöße)
              </Badge>
            )}
          </div>

          <div className="space-y-4">
            {results.map((r) => (
              <Card key={r.entity_type}>
                <CardHeader>
                  <CardTitle className="text-base">
                    {ENTITY_LABELS[r.entity_type] ?? r.entity_type}
                  </CardTitle>
                  <CardDescription>
                    {r.total_count === 0
                      ? 'Keine Verstöße gefunden'
                      : `${r.total_count} Verstoß(verstöße)`}
                  </CardDescription>
                </CardHeader>
                {r.violations.length > 0 && (
                  <CardContent>
                    <Table>
                      <TableHeader>
                        <TableRow>
                          <TableHead>Regel</TableHead>
                          <TableHead>ID</TableHead>
                          <TableHead>Detail</TableHead>
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        {r.violations.map((v, i) => (
                          <TableRow key={`${v.rule_id}-${v.entity_id ?? i}`}>
                            <TableCell className="font-mono text-xs">{v.rule_id}</TableCell>
                            <TableCell className="font-mono text-xs">
                              {v.entity_id ?? '–'}
                            </TableCell>
                            <TableCell>{v.detail}</TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </CardContent>
                )}
              </Card>
            ))}
          </div>
        </>
      )}
    </div>
  )
}
