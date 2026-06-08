import { Link } from '@/app/routing/react-router-compat'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
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

const TERMINOLOGY_TEXTS = {
  de: {
    title: 'Fachsprache Landhandel',
    description: 'Zentraler DE/EN-Begriffskatalog fuer Landhandel, CRM, DMS und Finance.',
    button: 'Terminologie oeffnen',
  },
  en: {
    title: 'Landhandel terminology',
    description: 'Central DE/EN glossary for landhandel, CRM, DMS and finance.',
    button: 'Open terminology',
  },
  es: {
    title: 'Terminologia Landhandel',
    description: 'Glosario central DE/EN para Landhandel, CRM, DMS y finanzas.',
    button: 'Abrir terminologia',
  },
} as const

export default function AdminSetupPage(): JSX.Element {
  const { i18n } = useTranslation()
  const lang = (i18n.language as keyof typeof SETUP_TEXTS) in SETUP_TEXTS
    ? (i18n.language as keyof typeof SETUP_TEXTS)
    : 'de'
  const texts = SETUP_TEXTS[lang]
  const terminology = TERMINOLOGY_TEXTS[lang] ?? TERMINOLOGY_TEXTS.de

  return (
    <div className="container mx-auto py-8 space-y-6">
      <div className="space-y-2">
        <h1 className="text-3xl font-bold">{texts.title}</h1>
        <p className="text-muted-foreground">{texts.subtitle}</p>
      </div>

      <div className="grid gap-6">
        <DmsIntegrationCard />
        <Card>
          <CardHeader>
            <CardTitle>{terminology.title}</CardTitle>
            <CardDescription>{terminology.description}</CardDescription>
          </CardHeader>
          <CardContent>
            <Button asChild>
              <Link to="/admin/terminologie">{terminology.button}</Link>
            </Button>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
