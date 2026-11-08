import { NativeSelect } from '@/components/ui/native-select'
import { schluesselText, useSteuerschluesselAuswahl, type Schluesselwahl, type Steuerrichtung } from '@/lib/api/steuerschluessel-auswahl'

/**
 * Auswahl eines Steuerschluessels — das Feld, das in Belegen und Stammdaten an die Stelle des
 * Prozentsatzes tritt. Es waehlt nichts vor: Ohne Auswahl bleibt der Wert leer.
 */
export function SteuerschluesselSelect({
  richtung,
  value,
  onChange,
  id,
  ariaLabel = 'Steuerschlüssel',
  disabled = false,
  className,
}: {
  richtung: Steuerrichtung
  value: string | null | undefined
  /** `wahl` ist der gewaehlte Schluessel mit seinem Satz, `null` bei leerer Auswahl. */
  onChange: (_code: string | null, _wahl: Schluesselwahl | null) => void
  id?: string
  ariaLabel?: string
  disabled?: boolean
  className?: string
}): JSX.Element {
  const auswahl = useSteuerschluesselAuswahl(richtung)
  const schluessel = auswahl.data ?? []
  const gewaehlt = value ?? ''
  const optionen = schluessel.map((k) => ({ value: k.code, label: schluesselText(schluessel, k.code) }))
  // Ein hinterlegter Schluessel, der nicht mehr gilt, bleibt sichtbar statt still zu verschwinden.
  if (gewaehlt && !auswahl.isLoading && !optionen.some((o) => o.value === gewaehlt)) {
    optionen.unshift({ value: gewaehlt, label: schluesselText(schluessel, gewaehlt) })
  }
  return (
    <>
      <NativeSelect
        id={id}
        className={className}
        value={gewaehlt}
        disabled={disabled || auswahl.isLoading}
        ariaLabel={ariaLabel}
        placeholder={
          auswahl.isLoading ? 'Lädt …'
            : auswahl.isError ? 'Steuerschlüssel nicht geladen'
              : schluessel.length === 0 ? 'Kein Steuerschlüssel eingerichtet'
                : 'Steuerschlüssel wählen'
        }
        options={optionen}
        onValueChange={(code) => onChange(code || null, schluessel.find((k) => k.code === code) ?? null)}
      />
      {auswahl.isError ? (
        <p className="text-xs text-status-error" role="alert">Steuerschlüssel konnten nicht geladen werden.</p>
      ) : null}
    </>
  )
}
