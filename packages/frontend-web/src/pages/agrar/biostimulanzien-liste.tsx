/**
 * Biostimulanzien-Liste Maske
 * ListReport für Biostimulanzien und sonstige Agrarprodukte mit Filter und Suche
 */

import { type JSX, useMemo, useState } from 'react';
import { type ColumnDef } from '@/components/ui/data-table';
import { useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { ListReport } from '@/components/patterns/ListReport';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Skeleton } from '@/components/ui/skeleton';
import { CheckCircle, XCircle, Edit, Eye } from 'lucide-react';

// API Client
const apiClient = {
  async getBiostimulanzienList(params: any = {}) {
    const queryString = new URLSearchParams(params).toString();
    const response = await fetch(`/api/v1/agrar/biostimulanzien?${queryString}`);
    if (!response.ok) throw new Error('Failed to fetch Biostimulanzien list');
    return response.json();
  },

  async getBiostimulanzienStats() {
    const response = await fetch('/api/v1/agrar/biostimulanzien/stats/overview');
    if (!response.ok) throw new Error('Failed to fetch stats');
    return response.json();
  },
};

interface BiostimulanzienItem {
  id: string;
  artikelnummer: string;
  name: string;
  typ: string;
  hersteller: string;
  eu_zulassung: string | null;
  ablauf_zulassung: string | null;
  vk_preis: number | null;
  lagerbestand: number;
  verfuegbar: number;
  ist_aktiv: boolean;
}

const buildColumns = (): ColumnDef<BiostimulanzienItem>[] => [
  {
    accessorKey: 'artikelnummer',
    header: 'Artikelnummer',
    cell: ({ row }): JSX.Element => (
      <span className="font-mono text-sm">{row.original.artikelnummer}</span>
    ),
  },
  {
    accessorKey: 'name',
    header: 'Name',
  },
  {
    accessorKey: 'typ',
    header: 'Typ',
    cell: ({ row }): JSX.Element => {
      const typ = row.original.typ;
      const typLabels: Record<string, string> = {
        'Biostimulanz': 'Biostimulanz',
        'Kalk': 'Kalk',
        'Substrat': 'Substrat',
        'Erde': 'Erde',
        'Sonstiges': 'Sonstiges',
      };
      return <Badge variant="outline">{typLabels[typ] || typ}</Badge>;
    },
  },
  {
    accessorKey: 'hersteller',
    header: 'Hersteller',
  },
  {
    accessorKey: 'zulassung',
    header: 'EU-Zulassung',
    cell: ({ row }): JSX.Element => {
      const item = row.original;
      if (item.eu_zulassung) {
        return (
          <Badge variant="secondary" className="bg-green-100 text-green-800">
            <CheckCircle className="w-3 h-3 mr-1" />
            {item.eu_zulassung}
          </Badge>
        );
      }
      return (
        <Badge variant="secondary" className="bg-gray-100 text-gray-600">
          <XCircle className="w-3 h-3 mr-1" />
          Keine
        </Badge>
      );
    },
  },
  {
    accessorKey: 'ablauf_zulassung',
    header: 'Ablauf Zulassung',
    cell: ({ row }): string => {
      const date = row.original.ablauf_zulassung;
      if (!date) return '-';
      const dateObj = new Date(date);
      const now = new Date();
      const isExpired = dateObj < now;
      const formatted = dateObj.toLocaleDateString('de-DE');
      return isExpired ? `${formatted} (abgelaufen)` : formatted;
    },
  },
  {
    accessorKey: 'lagerstatus',
    header: 'Lagerstatus',
    cell: ({ row }): JSX.Element => {
      const item = row.original;
      const available = item.verfuegbar || 0;

      if (!item.ist_aktiv) {
        return <Badge variant="secondary" className="bg-gray-100 text-gray-600">Inaktiv</Badge>;
      } else if (available <= 0) {
        return <Badge variant="destructive">Nicht verfügbar</Badge>;
      } else if (available < 50) {
        return <Badge variant="secondary" className="bg-yellow-100 text-yellow-800">Niedrig</Badge>;
      } else {
        return <Badge variant="secondary" className="bg-green-100 text-green-800">Verfügbar</Badge>;
      }
    },
  },
  {
    accessorKey: 'vk_preis',
    header: 'VK-Preis',
    cell: ({ row }): string => {
      const price = row.original.vk_preis;
      return price ? `€${price.toFixed(2)}` : '-';
    },
  },
  {
    accessorKey: 'actions',
    header: 'Aktionen',
    cell: ({ row }): JSX.Element => {
      const navigate = useNavigate();
      const item = row.original;

      return (
        <div className="flex gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => navigate(`/agrar/biostimulanzien-stamm/${item.id}`)}
          >
            <Eye className="w-4 h-4" />
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => navigate(`/agrar/biostimulanzien-stamm/${item.id}`)}
          >
            <Edit className="w-4 h-4" />
          </Button>
        </div>
      );
    },
  },
];

const BiostimulanzienListePage: React.FC = () => {
  const navigate = useNavigate();
  const [search, setSearch] = useState<string>('');

  // Queries
  const { data: biostimulanzienList, isLoading } = useQuery({
    queryKey: ['biostimulanzien-list'],
    queryFn: () => apiClient.getBiostimulanzienList({ limit: 100 }),
  });

  const columns = useMemo<ColumnDef<BiostimulanzienItem>[]>(() => buildColumns(), []);

  const filteredData = useMemo<BiostimulanzienItem[]>(() => {
    if (!Array.isArray(biostimulanzienList?.items)) return [];
    const term = search.trim().toLowerCase();
    if (term.length === 0) return biostimulanzienList.items;
    return biostimulanzienList.items.filter((item: BiostimulanzienItem) =>
      item.name.toLowerCase().includes(term) ||
      item.artikelnummer.toLowerCase().includes(term) ||
      item.typ.toLowerCase().includes(term) ||
      item.hersteller?.toLowerCase().includes(term)
    );
  }, [biostimulanzienList, search]);

  if (isLoading) {
    return (
      <div className="space-y-4 p-6">
        <Skeleton className="h-12 w-1/2" />
        <Skeleton className="h-10 w-full" />
        <Skeleton className="h-72 w-full" />
      </div>
    );
  }

  return (
    <ListReport
      title="Biostimulanzien-Verwaltung"
      subtitle="Übersicht aller Biostimulanzien und sonstiger Agrarprodukte"
      data={filteredData}
      columns={columns}
      primaryActions={[
        {
          id: 'create-biostimulanzien',
          label: 'Neues Produkt',
          onClick: (): void => navigate('/agrar/biostimulanzien-stamm'),
        },
      ]}
      overflowActions={[
        {
          id: 'export-biostimulanzien',
          label: 'Export CSV',
          onClick: (): void => {
            // placeholder for export functionality
          },
        },
      ]}
      searchPlaceholder="Biostimulanzien suchen (Name, Artikelnummer, Typ, Hersteller)"
      onSearch={setSearch}
      filterOptions={[
        {
          field: 'typ',
          label: 'Typ',
          type: 'select',
          options: [
            { value: 'Biostimulanz', label: 'Biostimulanz' },
            { value: 'Kalk', label: 'Kalk' },
            { value: 'Substrat', label: 'Substrat' },
            { value: 'Erde', label: 'Erde' },
            { value: 'Sonstiges', label: 'Sonstiges' },
          ],
        },
        {
          field: 'eu_zulassung',
          label: 'EU-Zulassung',
          type: 'select',
          options: [
            { value: 'exists', label: 'Vorhanden' },
            { value: 'none', label: 'Keine' },
          ],
        },
        {
          field: 'ist_aktiv',
          label: 'Status',
          type: 'select',
          options: [
            { value: 'true', label: 'Aktiv' },
            { value: 'false', label: 'Inaktiv' },
          ],
        },
      ]}
      selectable
      mcpContext={{
        pageDomain: 'agrar',
        currentDocument: 'biostimulanzien',
      }}
    />
  );
};

export default BiostimulanzienListePage;