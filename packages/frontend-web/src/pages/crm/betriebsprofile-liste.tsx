import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { DataTable } from '@/components/ui/data-table'
import { Input } from '@/components/ui/input'
import { FileDown, Plus, Search, Tractor, Loader2 } from 'lucide-react'
import { queryKeys } from '@/lib/query'
import { crmService, type FarmProfile } from '@/lib/services/crm-service'

export default function BetriebsprofileListePage(): JSX.Element {
  const navigate = useNavigate()
  const [searchTerm, setSearchTerm] = useState('')

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
      label: 'Betriebsname',
      render: (profile: FarmProfile) => (
        <button
          onClick={() => navigate(`/crm/betriebsprofil/${profile.id}`)}
          className="font-medium text-blue-600 hover:underline"
        >
          {profile.farmName}
        </button>
      ),
    },
    { key: 'owner' as const, label: 'Inhaber' },
    {
      key: 'totalArea' as const,
      label: 'Gesamtfläche',
      render: (profile: FarmProfile) => `${profile.totalArea.toFixed(2)} ha`,
    },
    {
      key: 'crops' as const,
      label: 'Kulturen',
      render: (profile: FarmProfile) => profile.crops?.length || 0,
    },
    {
      key: 'livestock' as const,
      label: 'Tierbestand',
      render: (profile: FarmProfile) => {
        const total = profile.livestock?.reduce((sum, l) => sum + (l.count || 0), 0) || 0
        return total > 0 ? `${total} Tiere` : '-'
      },
    },
    {
      key: 'certifications' as const,
      label: 'Zertifizierungen',
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

  if (error) {
    return (
      <div className="space-y-4 p-6">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-red-600">Fehler beim Laden der Betriebsprofile</h1>
          <p className="text-muted-foreground">
            {error instanceof Error ? error.message : 'Unbekannter Fehler'}
          </p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-4 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-2">
            <Tractor className="h-8 w-8 text-green-600" />
            Betriebsprofile
          </h1>
          <p className="text-muted-foreground">
            {isLoading ? 'Lade Betriebsprofile...' : `${totalProfiles} landwirtschaftliche Betriebe`}
          </p>
        </div>
        <Button onClick={() => navigate('/crm/betriebsprofil/neu')} className="gap-2">
          <Plus className="h-4 w-4" />
          Neues Betriebsprofil
        </Button>
      </div>

      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Betriebe Gesamt</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{totalProfiles}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Gesamtfläche</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">{totalArea.toFixed(0)} ha</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Ø Betriebsgröße</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{avgArea.toFixed(1)} ha</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Bio-Zertifiziert</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">{bioProfiles}</div>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Suche</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex gap-4">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <Input
                placeholder="Suche nach Betriebsname oder Inhaber..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10"
              />
            </div>
            <Button variant="outline" className="gap-2">
              <FileDown className="h-4 w-4" />
              Export
            </Button>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardContent className="pt-6">
          {isLoading ? (
            <div className="flex items-center justify-center py-8">
              <Loader2 className="h-8 w-8 animate-spin" />
              <span className="ml-2">Lade Betriebsprofile...</span>
            </div>
          ) : (
            <DataTable data={profiles} columns={columns} />
          )}
        </CardContent>
      </Card>
    </div>
  )
}

