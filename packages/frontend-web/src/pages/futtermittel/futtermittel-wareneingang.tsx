import { useState } from 'react'
import { useNavigate } from '@/app/routing/typed-router'
import { Wizard } from '@/components/mask-builder'
import { useMaskData } from '@/components/mask-builder/hooks'
import { WizardConfig } from '@/components/mask-builder/types'
import { validateFields } from '@/components/mask-builder/validation'
import { toast } from '@/hooks/use-toast'

const wareneingangWizardConfig: WizardConfig = {
  title: 'Futtermittel-Wareneingang',
  subtitle: 'QS-konforme Annahme und Chargenbildung nach EU 767/2009',
  type: 'wizard',
  steps: [
    {
      key: 'annahme',
      title: 'Wareneingang annehmen',
      description: 'Grunddaten und Lieferanteninformationen',
      fields: [
        {
          name: 'lieferantId',
          label: 'Lieferant',
          type: 'lookup',
          required: true,
          endpoint: '/api/v1/crm/business-partners?type=supplier',
          displayField: 'name',
          valueField: 'id'
        },
        {
          name: 'bestellungId',
          label: 'Bestellreferenz',
          type: 'lookup',
          endpoint: '/api/v1/futter/bestellungen?status=offen',
          displayField: 'nummer',
          valueField: 'id',
          helpText: 'Optional: Verknüpfung mit bestehender Bestellung'
        },
        {
          name: 'lagerort',
          label: 'Lagerort',
          type: 'select',
          required: true,
          options: [
            { value: 'silo-01', label: 'Silo 01 - Getreide' },
            { value: 'silo-02', label: 'Silo 02 - Ölsaaten' },
            { value: 'lager-03', label: 'Lager 03 - Mischfuttermittel' },
            { value: 'kuehl-04', label: 'Kühlhaus 04 - Proteine' }
          ]
        }
      ]
    },
    {
      key: 'chargen',
      title: 'Chargen bilden',
      description: 'Einzelne Chargen mit Qualitätsdaten erfassen',
      fields: [
        {
          name: 'positionen',
          label: 'Wareneingangspositionen',
          type: 'table',
          required: true,
          columns: [
            {
              key: 'futtermittelId',
              label: 'Futtermittel',
              type: 'lookup',
              required: true
            },
            {
              key: 'erwarteteMenge',
              label: 'Erwartet',
              type: 'number'
            },
            {
              key: 'gelieferteMenge',
              label: 'Geliefert',
              type: 'number',
              required: true
            },
            {
              key: 'einheit',
              label: 'Einheit',
              type: 'select',
              required: true
            },
            {
              key: 'chargenNummer',
              label: 'Charge-Nr.',
              type: 'text',
              required: true
            },
            {
              key: 'produktionsdatum',
              label: 'Produktion',
              type: 'date',
              required: true
            },
            {
              key: 'verfallsdatum',
              label: 'Verfall',
              type: 'date',
              required: true
            },
            {
              key: 'temperatur',
              label: 'Temperatur (°C)',
              type: 'number'
            },
            {
              key: 'phWert',
              label: 'pH-Wert',
              type: 'number'
            },
            {
              key: 'visuellerEindruck',
              label: 'Visueller Eindruck',
              type: 'select'
            },
            {
              key: 'geruch',
              label: 'Geruch',
              type: 'select'
            },
            {
              key: 'qsFreigabe',
              label: 'QS-Freigabe',
              type: 'boolean'
            }
          ] as any,
          helpText: 'Erfassen Sie jede Charge separat mit Qualitätsdaten'
        }
      ]
    },
    {
      key: 'labor',
      title: 'Laboranalyse',
      description: 'Qualitätskennzahlen und Grenzwertprüfung',
      fields: [
        {
          name: 'qualitaetspruefung.aflatoxin',
          label: 'Aflatoxin (µg/kg)',
          type: 'number',
          helpText: 'Grenzwert: 10 µg/kg'
        },
        {
          name: 'qualitaetspruefung.feuchtigkeit',
          label: 'Feuchtigkeit (%)',
          type: 'number',
          helpText: 'Grenzwert: 15%'
        },
        {
          name: 'qualitaetspruefung.rohprotein',
          label: 'Rohprotein (%)',
          type: 'number'
        },
        {
          name: 'qualitaetspruefung.rohfett',
          label: 'Rohfett (%)',
          type: 'number'
        },
        {
          name: 'qualitaetspruefung.rohfaser',
          label: 'Rohfaser (%)',
          type: 'number'
        },
        {
          name: 'qualitaetspruefung.rohasche',
          label: 'Rohasche (%)',
          type: 'number'
        },
        {
          name: 'qualitaetspruefung.freigabe',
          label: 'Qualitätsfreigabe',
          type: 'boolean',
          helpText: 'Alle Grenzwerte eingehalten?'
        }
      ]
    },
    {
      key: 'dokumentation',
      title: 'Dokumentation',
      description: 'Transportdokumente und abschließende Bemerkungen',
      fields: [
        {
          name: 'transportDokumente',
          label: 'Transportdokumente',
          type: 'file',
          helpText: 'Lieferscheine, QS-Zertifikate, Analysen'
        },
        {
          name: 'bemerkungen',
          label: 'Bemerkungen',
          type: 'textarea',
          placeholder: 'Zusätzliche Anmerkungen zur Wareneingangsprüfung...'
        }
      ]
    }
  ],
  actions: [
    {
      key: 'save-draft',
      label: 'Entwurf speichern',
      type: 'secondary',
      onClick: () => {}
    },
    {
      key: 'reject',
      label: 'Ablehnen',
      type: 'danger',
      onClick: () => {}
    },
    {
      key: 'approve',
      label: 'Wareneingang freigeben',
      type: 'primary',
      onClick: () => {}
    }
  ],
  api: {
    baseUrl: '/api/v1/futter/wareneingang',
    endpoints: {
      create: '/api/v1/futter/wareneingang',
      update: '/api/v1/futter/wareneingang/{id}'
    }
  },
  permissions: ['futtermittel.receive', 'quality.check', 'warehouse.manage'],
  onComplete: () => {} // Wird über Wizard-Props überschrieben
}

export default function FuttermittelWareneingangPage(): JSX.Element {
  const navigate = useNavigate()
  const [loading, setLoading] = useState(false)

  const { saveData } = useMaskData({
    apiUrl: wareneingangWizardConfig.api.baseUrl
  })

  const validate = (formData: any) => validateFields(wareneingangWizardConfig.steps.flatMap((step) => step.fields), formData ?? {})
  const showValidationToast = (errors: Record<string, string>) => {
    toast({ variant: 'destructive', title: 'Validierungsfehler', description: `${Object.keys(errors).length} Feld(er) muessen korrigiert werden.` })
  }

  const handleComplete = async (formData: any) => {
    const errors = validate(formData)
    if (Object.keys(errors).length > 0) {
      showValidationToast(errors)
      return
    }

    setLoading(true)
    try {
      await saveData({ ...formData, status: 'approved' })
      toast({ title: 'Wareneingang freigegeben', description: 'Der Wareneingang wurde erfolgreich freigegeben.' })
      navigate('/futtermittel/wareneingang')
    } catch (error) {
      toast({ title: 'Fehler', description: 'Wareneingang konnte nicht freigegeben werden.', variant: 'destructive' })
    } finally {
      setLoading(false)
    }
  }

  const handleCancel = () => {
    if (confirm('Wareneingang wirklich abbrechen? Nicht gespeicherte Daten gehen verloren.')) {
      navigate('/futtermittel')
    }
  }

  return (
    <Wizard
      config={wareneingangWizardConfig}
      onComplete={handleComplete}
      onCancel={handleCancel}
      isLoading={loading}
    />
  )
}