/**
 * Dünger-Liste Maske
 * ListReport für Dünger-Übersicht mit Filter und Suche
 */

import React, { useState, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Skeleton } from '@/components/ui/skeleton';
import { Plus, Search, Filter, Shield, Droplets, AlertTriangle, Edit, Eye, CheckCircle, XCircle, Info } from 'lucide-react';

// API Client mit Fehlerbehandlung
const apiClient = {
  async getDuengerList(params: any = {}) {
    try {
      const queryString = new URLSearchParams(params).toString();
      const response = await fetch(`/api/v1/agrar/duenger?${queryString}`);
      if (!response.ok) return { items: [], total: 0 };
      return response.json();
    } catch (_error) {
      // API nicht erreichbar - leere Liste zurückgeben
      return { items: [], total: 0 };
    }
  },

  async getDuengerStats() {
    try {
      const response = await fetch('/api/v1/agrar/duenger/stats/overview');
      if (!response.ok) return null;
      return response.json();
    } catch (_error) {
      // API nicht erreichbar - null zurückgeben
      return null;
    }
  },
};

const DuengerListePage: React.FC = () => {
  const navigate = useNavigate();

  // Filter State
  const [searchTerm, setSearchTerm] = useState('');
  const [typFilter, setTypFilter] = useState('');
  const [herstellerFilter, setHerstellerFilter] = useState('');
  const [kulturTypFilter, setKulturTypFilter] = useState('');
  const [safetyFilter, setSafetyFilter] = useState('');

  // Queries
  const { data: duengerList, isLoading } = useQuery({
    queryKey: ['duenger-list', searchTerm, typFilter, herstellerFilter, kulturTypFilter, safetyFilter],
    queryFn: () => apiClient.getDuengerList({
      search: searchTerm || undefined,
      typ: typFilter && typFilter !== 'all-types' ? typFilter : undefined,
      hersteller: herstellerFilter || undefined,
      kultur_typ: kulturTypFilter && kulturTypFilter !== 'all-kultur' ? kulturTypFilter : undefined,
      limit: 100,
    }),
  });

  const { data: stats } = useQuery({
    queryKey: ['duenger-stats'],
    queryFn: apiClient.getDuengerStats,
  });

  // Filtered data
  const filteredData = useMemo(() => {
    if (!duengerList?.items) return [];

    let filtered = duengerList.items;

    // Additional client-side filtering for safety
    if (safetyFilter && safetyFilter !== 'all-safety') {
      filtered = filtered.filter((item: any) => {
        if (safetyFilter === 'wassergefaehrdend') {
          return item.wassergefaehrdend;
        } else if (safetyFilter === 'gefahrstoff') {
          return item.gefahrstoff_klasse;
        } else if (safetyFilter === 'safe') {
          return !item.wassergefaehrdend && !item.gefahrstoff_klasse;
        }
        return true;
      });
    }

    return filtered;
  }, [duengerList, safetyFilter]);

  const handleNewDuenger = () => {
    navigate('/agrar/duenger-stamm');
  };

  const handleEditDuenger = (id: string) => {
    navigate(`/agrar/duenger-stamm/${id}`);
  };

  const handleViewDuenger = (id: string) => {
    navigate(`/agrar/duenger-stamm/${id}`);
  };

  const getSafetyBadges = (item: any) => {
    const badges = [];

    if (item.gefahrstoff_klasse) {
      badges.push(
        <Badge key="danger" variant="destructive" className="flex items-center gap-1">
          <Shield className="w-3 h-3" />
          {item.gefahrstoff_klasse}
        </Badge>
      );
    }

    if (item.wassergefaehrdend) {
      badges.push(
        <Badge key="water" variant="secondary" className="bg-blue-100 text-blue-800 flex items-center gap-1">
          <Droplets className="w-3 h-3" />
          WG
        </Badge>
      );
    }

    if (item.lagerklasse) {
      badges.push(
        <Badge key="storage" variant="outline" className="flex items-center gap-1">
          <AlertTriangle className="w-3 h-3" />
          {item.lagerklasse}
        </Badge>
      );
    }

    if (badges.length === 0) {
      badges.push(
        <Badge key="safe" variant="secondary" className="bg-green-100 text-green-800">
          Sicher
        </Badge>
      );
    }

    return badges;
  };

  const getApprovalStatus = (item: any) => {
    const hasDmv = item.dmv_nummer;
    const hasEu = item.eu_zulassung;
    const expiryDate = item.ablauf_zulassung ? new Date(item.ablauf_zulassung) : null;
    const isExpired = expiryDate && expiryDate < new Date();

    if (isExpired) {
      return (
        <Badge variant="destructive" className="flex items-center gap-1">
          <XCircle className="w-3 h-3" />
          Abgelaufen
        </Badge>
      );
    }

    if (hasDmv || hasEu) {
      return (
        <Badge variant="secondary" className="bg-green-100 text-green-800 flex items-center gap-1">
          <CheckCircle className="w-3 h-3" />
          {hasDmv && hasEu ? 'DüMV + EU' : hasDmv ? 'DüMV' : 'EU'}
        </Badge>
      );
    }

    return (
      <Badge variant="secondary" className="bg-gray-100 text-gray-600">
        Keine Zulassung
      </Badge>
    );
  };

  const getNPKDisplay = (item: any) => {
    const n = item.n_gehalt || 0;
    const p = item.p_gehalt || 0;
    const k = item.k_gehalt || 0;

    if (n === 0 && p === 0 && k === 0) {
      return '-';
    }

    return `${n}-${p}-${k}`;
  };

  const clearFilters = () => {
    setSearchTerm('');
    setTypFilter('');
    setHerstellerFilter('');
    setKulturTypFilter('');
    setSafetyFilter('');
  };

  return (
    <div className="p-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold">Dünger-Verwaltung</h1>
          <p className="text-muted-foreground">
            Übersicht aller Dünger und deren Eigenschaften
          </p>
        </div>
        <Button onClick={handleNewDuenger}>
          <Plus className="w-4 h-4 mr-2" />
          Neuer Dünger
        </Button>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        {isLoading ? (
          // Skeleton-Loading für KPI-Karten
          [...Array(4)].map((_, i) => (
            <Card key={i}>
              <CardHeader className="pb-2">
                <Skeleton className="h-4 w-1/2" />
              </CardHeader>
              <CardContent>
                <Skeleton className="h-8 w-3/4" />
              </CardContent>
            </Card>
          ))
        ) : (
          <>
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium">Gesamt Dünger</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{stats?.total_duenger || 0}</div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium">Wassergefährdend</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-blue-600">
                  {stats?.by_safety?.['WG'] || 0}
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium">Gefahrstoffe</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-red-600">
                  {stats?.by_safety?.['GHS+GHS'] || 0}
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium">Gesamtlagerwert</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  €{(stats?.stock_summary?.total_stock || 0).toLocaleString('de-DE', { minimumFractionDigits: 2 })}
                </div>
              </CardContent>
            </Card>
          </>
        )}
      </div>

      {/* Info wenn keine Daten vorhanden */}
      {!isLoading && filteredData.length === 0 && (
        <Alert className="mb-6">
          <Info className="h-4 w-4" />
          <AlertTitle>Vorschau-Modus</AlertTitle>
          <AlertDescription>
            Es sind noch keine Dünger-Daten verfügbar. Legen Sie Dünger-Artikel an, um die Übersicht zu füllen.
          </AlertDescription>
        </Alert>
      )}

      {/* Filters */}
      <Card className="mb-6">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Filter className="w-4 h-4" />
            Filter
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-6 gap-4">
            <div className="relative">
              <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Suche..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-9"
              />
            </div>

            <Select value={typFilter} onValueChange={setTypFilter}>
              <SelectTrigger>
                <SelectValue placeholder="Typ" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all-types">Alle</SelectItem>
                <SelectItem value="Mineraldünger">Mineraldünger</SelectItem>
                <SelectItem value="Organischer Dünger">Organischer Dünger</SelectItem>
                <SelectItem value="Organisch-Mineralischer Dünger">Organisch-Mineralischer Dünger</SelectItem>
                <SelectItem value="Kalkdünger">Kalkdünger</SelectItem>
              </SelectContent>
            </Select>

            <Select value={kulturTypFilter} onValueChange={setKulturTypFilter}>
              <SelectTrigger>
                <SelectValue placeholder="Kulturtyp" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all-kultur">Alle</SelectItem>
                <SelectItem value="Getreide">Getreide</SelectItem>
                <SelectItem value="Mais">Mais</SelectItem>
                <SelectItem value="Raps">Raps</SelectItem>
                <SelectItem value="Grünland">Grünland</SelectItem>
                <SelectItem value="Gemüse">Gemüse</SelectItem>
                <SelectItem value="Obst">Obst</SelectItem>
              </SelectContent>
            </Select>

            <Select value={safetyFilter} onValueChange={setSafetyFilter}>
              <SelectTrigger>
                <SelectValue placeholder="Sicherheit" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all-safety">Alle</SelectItem>
                <SelectItem value="safe">Sicher</SelectItem>
                <SelectItem value="wassergefaehrdend">Wassergefährdend</SelectItem>
                <SelectItem value="gefahrstoff">Gefahrstoff</SelectItem>
              </SelectContent>
            </Select>

            <Button variant="outline" onClick={clearFilters}>
              Filter löschen
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Table */}
      <Card>
        <CardHeader>
          <CardTitle>Dünger-Liste</CardTitle>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            // Skeleton-Loading für Tabelle
            <div className="space-y-4">
              {[...Array(5)].map((_, i) => (
                <Skeleton key={i} className="h-12 w-full" />
              ))}
            </div>
          ) : filteredData.length === 0 ? (
            <div className="text-center py-8 text-muted-foreground">
              <p className="mb-4">Keine Dünger-Einträge gefunden</p>
              <Button onClick={handleNewDuenger}>
                <Plus className="w-4 h-4 mr-2" />
                Ersten Dünger anlegen
              </Button>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Artikelnummer</TableHead>
                    <TableHead>Name</TableHead>
                    <TableHead>Typ</TableHead>
                    <TableHead>Hersteller</TableHead>
                    <TableHead>NPK</TableHead>
                    <TableHead>Zulassungen</TableHead>
                    <TableHead>Sicherheit</TableHead>
                    <TableHead>Lagerbestand</TableHead>
                    <TableHead>VK-Preis</TableHead>
                    <TableHead>Aktionen</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {filteredData.map((item: any) => (
                    <TableRow key={item.id}>
                      <TableCell className="font-medium">{item.artikelnummer}</TableCell>
                      <TableCell>{item.name}</TableCell>
                      <TableCell>{item.typ}</TableCell>
                      <TableCell>{item.hersteller}</TableCell>
                      <TableCell className="font-mono">{getNPKDisplay(item)}</TableCell>
                      <TableCell>{getApprovalStatus(item)}</TableCell>
                      <TableCell>
                        <div className="flex gap-1 flex-wrap">
                          {getSafetyBadges(item)}
                        </div>
                      </TableCell>
                      <TableCell className="text-right">
                        {item.lagerbestand?.toLocaleString('de-DE', { minimumFractionDigits: 2 }) || '0.00'} kg
                      </TableCell>
                      <TableCell>
                        {item.vk_preis ? `€${item.vk_preis.toFixed(2)}` : '-'}
                      </TableCell>
                      <TableCell>
                        <div className="flex gap-2">
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => handleViewDuenger(item.id)}
                          >
                            <Eye className="w-4 h-4" />
                          </Button>
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => handleEditDuenger(item.id)}
                          >
                            <Edit className="w-4 h-4" />
                          </Button>
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default DuengerListePage;