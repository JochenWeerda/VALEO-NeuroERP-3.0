import { useQuery } from '@tanstack/react-query'
import { BookOpen, Globe2, Languages, Search, ShieldCheck } from 'lucide-react'
import { useState } from 'react'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { ErrorState, LoadingState, EmptyState } from '@/components/ErrorState'
import { apiClient } from '@/lib/api-client'

type TerminologyRule = {
  rule_key: string
  title_de: string
  title_en: string
  description_de: string
  description_en: string
  examples: string[]
}

type TerminologyEntry = {
  term_key: string
  domain: string
  canonical_de: string
  canonical_en: string
  description_de: string
  description_en: string
  synonyms_de: string[]
  synonyms_en: string[]
  avoid_de: string[]
  avoid_en: string[]
  usage_notes_de: string[]
  usage_notes_en: string[]
  related_terms: string[]
  module_refs: string[]
  match_score?: number
  matched_fields?: string[]
}

type TerminologyRegistry = {
  schema_version: number
  manifest_kind: string
  generated_at: string
  query?: string | null
  domain?: string | null
  term_count: number
  domains: string[]
  languages: string[]
  global_rules: TerminologyRule[]
  terms: TerminologyEntry[]
}

const TEXTS = {
  de: {
    title: 'Fachsprache Landhandel',
    subtitle: 'Kanonischer DE/EN-Begriffskatalog fuer Landhandel, CRM, DMS und Finance.',
    searchLabel: 'Suche',
    searchPlaceholder: 'Begriff, Synonym oder Modul suchen',
    domainLabel: 'Bereich',
    allDomains: 'Alle Bereiche',
    summaryTerms: 'Begriffe',
    summaryDomains: 'Bereiche',
    summaryLanguages: 'Sprachen',
    summaryRules: 'Leitregeln',
    tableKey: 'Schluessel',
    tableGerman: 'Deutsch',
    tableEnglish: 'English',
    tableSynonyms: 'Synonyme / Alias',
    tableAvoid: 'Vermeiden',
    tableNotes: 'Hinweise',
    tableModules: 'Module',
    emptyTitle: 'Keine Begriffe gefunden',
    emptyMessage: 'Die Suche liefert keine Treffer. Versuche einen anderen Begriff oder waehle einen Bereich.',
    rulesTitle: 'Terminologie-Leitregeln',
    rulesSubtitle: 'Diese Regeln halten DE/EN-Fachsprache und UI-Begriffe synchron.',
  },
  en: {
    title: 'Landhandel terminology',
    subtitle: 'Canonical DE/EN glossary for landhandel, CRM, DMS and finance.',
    searchLabel: 'Search',
    searchPlaceholder: 'Search by term, synonym or module',
    domainLabel: 'Domain',
    allDomains: 'All domains',
    summaryTerms: 'Terms',
    summaryDomains: 'Domains',
    summaryLanguages: 'Languages',
    summaryRules: 'Rules',
    tableKey: 'Key',
    tableGerman: 'German',
    tableEnglish: 'English',
    tableSynonyms: 'Synonyms / aliases',
    tableAvoid: 'Avoid',
    tableNotes: 'Notes',
    tableModules: 'Modules',
    emptyTitle: 'No terms found',
    emptyMessage: 'The search has no matches. Try another term or pick a domain.',
    rulesTitle: 'Terminology rules',
    rulesSubtitle: 'These rules keep DE/EN business language and UI terms in sync.',
  },
} as const

function getLanguage(): keyof typeof TEXTS {
  if (typeof document !== 'undefined' && document.documentElement.lang.toLowerCase().startsWith('en')) {
    return 'en'
  }
  if (typeof window !== 'undefined') {
    const stored = window.localStorage.getItem('valeo-language')
    if (stored && stored.toLowerCase().startsWith('en')) {
      return 'en'
    }
  }
  return 'de'
}

function joinList(values: string[]): string {
  return values.length > 0 ? values.join(' · ') : '—'
}

export default function TerminologiePage(): JSX.Element {
  const lang = getLanguage()
  const texts = TEXTS[lang]
  const [query, setQuery] = useState('')
  const [domain, setDomain] = useState<string>('all')

  const registryQuery = useQuery({
    queryKey: ['admin', 'terminology-registry', domain, query],
    queryFn: async () => {
      const params: Record<string, string> = {}
      if (domain !== 'all') {
        params.domain = domain
      }
      if (query.trim()) {
        params.q = query.trim()
      }
      return (await apiClient.get<TerminologyRegistry>('/api/v1/terminology/registry', { params })).data
    },
  })

  if (registryQuery.isLoading) {
    return <LoadingState message="Terminologie-Katalog wird geladen..." />
  }

  if (registryQuery.isError || !registryQuery.data) {
    return <ErrorState error={registryQuery.error as Error} onRetry={() => void registryQuery.refetch()} />
  }

  const registry = registryQuery.data
  const terms = registry.terms
  const isFiltered = Boolean(query.trim()) || domain !== 'all'
  const domainOptions = registry.domains

  return (
    <div className="space-y-6 p-6">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div className="space-y-2">
          <h1 className="flex items-center gap-2 text-2xl font-semibold">
            <Languages className="h-6 w-6" />
            {texts.title}
          </h1>
          <p className="max-w-3xl text-sm text-muted-foreground">{texts.subtitle}</p>
        </div>
        <Badge variant="outline" className="gap-1.5">
          <ShieldCheck className="h-3.5 w-3.5" />
          {registry.manifest_kind}
        </Badge>
      </div>

      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardContent className="flex items-center justify-between p-4">
            <div>
              <p className="text-sm text-muted-foreground">{texts.summaryTerms}</p>
              <p className="text-2xl font-semibold">{registry.term_count}</p>
            </div>
            <BookOpen className="h-5 w-5 text-muted-foreground" />
          </CardContent>
        </Card>
        <Card>
          <CardContent className="flex items-center justify-between p-4">
            <div>
              <p className="text-sm text-muted-foreground">{texts.summaryDomains}</p>
              <p className="text-2xl font-semibold">{registry.domains.length}</p>
            </div>
            <Globe2 className="h-5 w-5 text-muted-foreground" />
          </CardContent>
        </Card>
        <Card>
          <CardContent className="flex items-center justify-between p-4">
            <div>
              <p className="text-sm text-muted-foreground">{texts.summaryLanguages}</p>
              <p className="text-2xl font-semibold">{registry.languages.join(' / ')}</p>
            </div>
            <Languages className="h-5 w-5 text-muted-foreground" />
          </CardContent>
        </Card>
        <Card>
          <CardContent className="flex items-center justify-between p-4">
            <div>
              <p className="text-sm text-muted-foreground">{texts.summaryRules}</p>
              <p className="text-2xl font-semibold">{registry.global_rules.length}</p>
            </div>
            <ShieldCheck className="h-5 w-5 text-muted-foreground" />
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Search className="h-5 w-5" />
            {texts.searchLabel}
          </CardTitle>
        </CardHeader>
        <CardContent className="grid gap-4 md:grid-cols-[1.8fr_0.8fr]">
          <div className="space-y-2">
            <label className="text-sm font-medium">{texts.searchLabel}</label>
            <Input
              value={query}
              onChange={(event) => setQuery(event.target.value)}
              placeholder={texts.searchPlaceholder}
            />
          </div>
          <div className="space-y-2">
            <label className="text-sm font-medium">{texts.domainLabel}</label>
            <Select value={domain} onValueChange={setDomain}>
              <SelectTrigger>
                <SelectValue placeholder={texts.allDomains} />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">{texts.allDomains}</SelectItem>
                {domainOptions.map((item) => (
                  <SelectItem key={item} value={item}>
                    {item}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>{texts.rulesTitle}</CardTitle>
          <p className="text-sm text-muted-foreground">{texts.rulesSubtitle}</p>
        </CardHeader>
        <CardContent className="grid gap-3 md:grid-cols-2">
          {registry.global_rules.map((rule) => (
            <div key={rule.rule_key} className="rounded-lg border p-4">
              <p className="text-sm font-semibold">{lang === 'de' ? rule.title_de : rule.title_en}</p>
              <p className="mt-1 text-sm text-muted-foreground">
                {lang === 'de' ? rule.description_de : rule.description_en}
              </p>
              <p className="mt-2 text-xs text-muted-foreground">
                {joinList(rule.examples)}
              </p>
            </div>
          ))}
        </CardContent>
      </Card>

      {terms.length === 0 ? (
        <EmptyState title={texts.emptyTitle} message={texts.emptyMessage} />
      ) : (
        <Card>
          <CardHeader>
            <CardTitle>Registry</CardTitle>
          </CardHeader>
          <CardContent>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>{texts.tableKey}</TableHead>
                  <TableHead>{texts.tableGerman}</TableHead>
                  <TableHead>{texts.tableEnglish}</TableHead>
                  <TableHead>{texts.tableSynonyms}</TableHead>
                  <TableHead>{texts.tableAvoid}</TableHead>
                  <TableHead>{texts.tableNotes}</TableHead>
                  <TableHead>{texts.tableModules}</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {terms.map((term) => (
                  <TableRow key={term.term_key}>
                    <TableCell className="align-top font-medium">
                      <div className="space-y-1">
                        <div>{term.term_key}</div>
                        <Badge variant="outline">{term.domain}</Badge>
                        {typeof term.match_score === 'number' && isFiltered ? (
                          <Badge variant="secondary">Score {term.match_score}</Badge>
                        ) : null}
                      </div>
                    </TableCell>
                    <TableCell className="align-top">
                      <div className="space-y-1">
                        <div className="font-medium">{term.canonical_de}</div>
                        <p className="text-xs text-muted-foreground">{term.description_de}</p>
                      </div>
                    </TableCell>
                    <TableCell className="align-top">
                      <div className="space-y-1">
                        <div className="font-medium">{term.canonical_en}</div>
                        <p className="text-xs text-muted-foreground">{term.description_en}</p>
                      </div>
                    </TableCell>
                    <TableCell className="align-top text-xs text-muted-foreground">
                      <div className="space-y-2">
                        <div>
                          <span className="font-medium text-foreground">DE:</span> {joinList(term.synonyms_de)}
                        </div>
                        <div>
                          <span className="font-medium text-foreground">EN:</span> {joinList(term.synonyms_en)}
                        </div>
                      </div>
                    </TableCell>
                    <TableCell className="align-top text-xs text-muted-foreground">
                      <div className="space-y-2">
                        <div>
                          <span className="font-medium text-foreground">DE:</span> {joinList(term.avoid_de)}
                        </div>
                        <div>
                          <span className="font-medium text-foreground">EN:</span> {joinList(term.avoid_en)}
                        </div>
                      </div>
                    </TableCell>
                    <TableCell className="align-top text-xs text-muted-foreground">
                      <div className="space-y-2">
                        <div>
                          <span className="font-medium text-foreground">DE:</span> {joinList(term.usage_notes_de)}
                        </div>
                        <div>
                          <span className="font-medium text-foreground">EN:</span> {joinList(term.usage_notes_en)}
                        </div>
                        {term.matched_fields?.length ? (
                          <div>
                            <span className="font-medium text-foreground">Match:</span> {term.matched_fields.join(', ')}
                          </div>
                        ) : null}
                      </div>
                    </TableCell>
                    <TableCell className="align-top text-xs text-muted-foreground">
                      <div className="whitespace-pre-line">
                        {term.module_refs.length > 0 ? term.module_refs.join(' · ') : '—'}
                      </div>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
