import { useTranslation } from 'react-i18next'
import DmsIntegrationCard from './dms-integration'

const SETUP_TEXTS = {
  de: {
    title: 'Ersteinrichtung',
    subtitle: 'Konfigurieren Sie die wichtigsten Integrationen f\u00fcr VALEO NeuroERP.',
  },
  en: {
    title: 'Initial Setup',
    subtitle: 'Configure the most important integrations for VALEO NeuroERP.',
  },
  es: {
    title: 'Configuraci\u00f3n Inicial',
    subtitle: 'Configure las integraciones m\u00e1s importantes para VALEO NeuroERP.',
  },
} as const

export default function AdminSetupPage(): JSX.Element {
  const { i18n } = useTranslation()
  const lang = (i18n.language as keyof typeof SETUP_TEXTS) in SETUP_TEXTS
    ? (i18n.language as keyof typeof SETUP_TEXTS)
    : 'de'
  const texts = SETUP_TEXTS[lang]

  return (
    <div className="container mx-auto py-8 space-y-6">
      <div className="space-y-2">
        <h1 className="text-3xl font-bold">{texts.title}</h1>
        <p className="text-muted-foreground">{texts.subtitle}</p>
      </div>

      <div className="grid gap-6">
        <DmsIntegrationCard />
      </div>
    </div>
  )
}
