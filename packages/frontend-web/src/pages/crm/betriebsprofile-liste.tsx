import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { useQuery } from '@tanstack/react-query'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { DataTable } from '@/components/ui/data-table'
import { Input } from '@/components/ui/input'
import { Skeleton } from '@/components/ui/skeleton'
import { FileDown, Plus, Search, Tractor, AlertCircle } from 'lucide-react'
import { queryKeys } from '@/lib/query'
import { crmService, type FarmProfile } from '@/lib/services/crm-service'
import { getEntityTypeLabel, getListTitle } from '@/features/crud/utils/i18n-helpers'

export default function BetriebsprofileListePage(): JSX.Element {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const [searchTerm, setSearchTerm] = useState('')
  const entityType = 'farmProfile'
  const entityTypeLabel = getEntityTypeLabel(t, entityType, 'Betriebsprofil')

  const { data: profilesData, isLoading, error } = useQuery({
    queryKey: queryKeys.crm.farmProfiles.list(),
    queryFn: () => crmService.getFarmProfiles({ search: searchTerm || undefined }),
  })

  const profiles = profilesData?.data || []
  const totalProfiles = profilesData?.total || 0
  const totalArea = profiles.reduce((sum, p) => sum + (p.totalArea || 0), 0)
  const avgArea = totalProfiles > 0 ? totalArea / totalProfiles : 0
  const bioProfiles = profiles.filter(p => p.certifications?.includes('Bio')).length

  const columns = [
    {
      key: 'farmName' as const,
      label: t('crud.fields.farmName'),
      render: (profile: FarmProfile) => (
        <button
          onClick={() => navigate(`/crm/betriebsprofil/${profile.id}`)}
          className="font-medium text-blue-600 hover:underline"
        >
          {profile.farmName}
        </button>
      ),
    },
    { key: 'owner' as const, label: t('crud.fields.owner') },
    {
      key: 'totalArea' as const,
      label: t('crud.fields.totalArea'),
      render: (profile: FarmProfile) => `${(profile.totalArea || 0).toFixed(2)} ha`,
    },
    {
      key: 'crops' as const,
      label: t('crud.fields.crops'),
      render: (profile: FarmProfile) => profile.crops?.length || 0,
    },
    {
      key: 'livestock' as const,
      label: t('crud.fields.livestock'),
      render: (profile: FarmProfile) => {
        const total = profile.livestock?.reduce((sum, l) => sum + (l.count || 0), 0) || 0
        return total > 0 ? `${total} ${t('crud.fields.animals')}` : '-'
      },
    },
    {
      key: 'certifications' as const,
      label: t('crud.fields.certifications'),
      render: (profile: FarmProfile) => (
        <div className="flex gap-1 flex-wrap">
          {profile.certifications?.slice(0, 3).map(cert => (
            <Badge key={cert} variant="outline" className="text-xs">
              {cert}
            </Badge>
          ))}
          {profile.certifications && profile.certifications.length > 3 && (
            <Badge variant="outline" className="text-xs">
              +{profile.certifications.length - 3}
            </Badge>
          )}
        </div>
      ),
    },
  ]

  // Skeleton-Komponente für KPI-Karten
  const KpiCardSkeleton = () => (
    <Card>
      <CardHeader className="pb-2">
        <CardTitle className="text-sm font-medium">
          <Skeleton className="h-4 w-24" />
        </CardTitle>
      </CardHeader>
      <CardContent>
        <Skeleton className="h-8 w-16" />
      </CardContent>
    </Card>
  )

  // Skeleton-Komponente für Tabelle
  const TableSkeleton = () => (
    <div className="space-y-3">
      <div className="flex gap-4 border-b pb-3">
        {columns.map((col, i) => (
          <Skeleton key={i} className="h-4 w-24" />
        ))}
      </div>
      {[...Array(5)].map((_, rowIdx) => (
        <div key={rowIdx} className="flex gap-4 py-3 border-b">
          {columns.map((_, colIdx) => (
            <Skeleton key={colIdx} className="h-4 w-20" />
          ))}
        </div>
      ))}
    </div>
  )

  if (error) {
    return (
      <div className="space-y-4 p-6">
        <div className="flex items-center gap-2">
          <Tractor className="h-8 w-8 text-green-600" />
          <h1 className="text-3xl font-bold">{getListTitle(t, entityTypeLabel)}</h1>
        </div>
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertTitle>{t('crud.messages.loadError')}</AlertTitle>
          <AlertDescription>
            {error instanceof Error ? error.message : t('common.unknownError')}
          </AlertDescription>
        </Alert>
      </div>
    )
  }

  return (
    <div className="space-y-4 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-2">
            <Tractor className="h-8 w-8 text-green-600" />
            {getListTitle(t, entityTypeLabel)}
          </h1>
          <div className="text-muted-foreground text-sm">
            {isLoading ? (
              <Skeleton className="h-4 w-32 mt-1" />
            ) : (
              t('crud.list.total', { count: totalProfiles, entityType: t('crud.fields.farms') })
            )}
          </div>
        </div>
        <Button onClick={() => navigate('/crm/betriebsprofil/neu')} className="gap-2">
          <Plus className="h-4 w-4" />
          Neues {entityTypeLabel}
        </Button>
      </div>

      {/* KPI-Karten mit Skeleton-Loading */}
      <div className="grid gap-4 md:grid-cols-4">
        {isLoading ? (
          <>
            <KpiCardSkeleton />
            <KpiCardSkeleton />
            <KpiCardSkeleton />
            <KpiCardSkeleton />
          </>
        ) : (
          <>
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium">{t('crud.fields.totalFarms')}</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{totalProfiles}</div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium">{t('crud.fields.totalArea')}</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-green-600">{totalArea.toFixed(0)} {t('crud.fields.hectares')}</div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium">{t('crud.fields.averageFarmSize')}</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{avgArea.toFixed(1)} {t('crud.fields.hectares')}</div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium">{t('crud.fields.organicCertified')}</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-green-600">{bioProfiles}</div>
              </CardContent>
            </Card>
          </>
        )}
      </div>

      {/* Info-Alert wenn keine Daten */}
      {!isLoading && profiles.length === 0 && (
        <Alert>
          <AlertCircle className="h-4 w-4" />
          <AlertTitle>Keine Betriebsprofile vorhanden</AlertTitle>
          <AlertDescription>
            Es sind noch keine Betriebsprofile angelegt. Klicken Sie auf &quot;Neues Betriebsprofil&quot;, um das erste Profil zu erstellen.
          </AlertDescription>
        </Alert>
      )}

      <Card>
        <CardHeader>
          <CardTitle>{t('common.search')}</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex gap-4">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <Input
                placeholder={t('crud.tooltips.placeholders.searchFarmNameOrOwner')}
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10"
              />
            </div>
            <Button variant="outline" className="gap-2">
              <FileDown className="h-4 w-4" />
              {t('crud.actions.export')}
            </Button>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardContent className="pt-6">
          {isLoading ? (
            <TableSkeleton />
          ) : (
            <DataTable data={profiles} columns={columns} />
          )}
        </CardContent>
      </Card>
    </div>
  )
}

