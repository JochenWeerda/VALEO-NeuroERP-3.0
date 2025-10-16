/**
 * Saatgut-Liste Maske
 * ListReport für Saatgut-Übersicht mit Filter und Suche
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
  async getSaatgutList(params: any = {}) {
    const queryString = new URLSearchParams(params).toString();
    const response = await fetch(`/api/v1/agrar/saatgut?${queryString}`);
    if (!response.ok) throw new Error('Failed to fetch Saatgut list');
    return response.json();
  },

  async getSaatgutStats() {
    const response = await fetch('/api/v1/agrar/saatgut/stats/overview');
    if (!response.ok) throw new Error('Failed to fetch stats');
    return response.json();
  },
};

interface SaatgutItem {
  id: string;
  artikelnummer: string;
  name: string;
  sorte: string;
  art: string;
  zuechter: string;
  bsa_zulassung: boolean;
  eu_zulassung: boolean;
  vk_preis: number | null;
  lagerbestand: number;
  reserviert: number;
  verfuegbar: number;
}

const buildColumns = (): ColumnDef<SaatgutItem>[] => [
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
    accessorKey: 'sorte',
    header: 'Sorte',
  },
  {
    accessorKey: 'art',
    header: 'Art',
  },
  {
    accessorKey: 'zuechter',
    header: 'Züchter',
  },
  {
    accessorKey: 'zulassungen',
    header: 'Zulassungen',
    cell: ({ row }): JSX.Element => {
      const item = row.original;
      const badges = [];
      if (item.bsa_zulassung) {
        badges.push(
          <Badge key="bsa" variant="secondary" className="bg-green-100 text-green-800">
            <CheckCircle className="w-3 h-3 mr-1" />
            BSA
          </Badge>
        );
      }
      if (item.eu_zulassung) {
        badges.push(
          <Badge key="eu" variant="secondary" className="bg-blue-100 text-blue-800">
            <CheckCircle className="w-3 h-3 mr-1" />
            EU
          </Badge>
        );
      }
      if (!item.bsa_zulassung && !item.eu_zulassung) {
        badges.push(
          <Badge key="none" variant="secondary" className="bg-gray-100 text-gray-600">
            <XCircle className="w-3 h-3 mr-1" />
            Keine Zulassung
          </Badge>
        );
      }
      return <div className="flex gap-1 flex-wrap">{badges}</div>;
    },
  },
  {
    accessorKey: 'lagerstatus',
    header: 'Lagerstatus',
    cell: ({ row }): JSX.Element => {
      const item = row.original;
      const available = item.verfuegbar || 0;

      if (available <= 0) {
        return <Badge variant="destructive">Nicht verfügbar</Badge>;
      } else if (available < 100) {
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
            onClick={() => navigate(`/agrar/saatgut-stamm/${item.id}`)}
          >
            <Eye className="w-4 h-4" />
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => navigate(`/agrar/saatgut-stamm/${item.id}`)}
          >
            <Edit className="w-4 h-4" />
          </Button>
        </div>
      );
    },
  },
];

const SaatgutListePage: React.FC = () => {
  const navigate = useNavigate();
  const [search, setSearch] = useState<string>('');

  // Queries
  const { data: saatgutList, isLoading } = useQuery({
    queryKey: ['saatgut-list'],
    queryFn: () => apiClient.getSaatgutList({ limit: 100 }),
  });


  const columns = useMemo<ColumnDef<SaatgutItem>[]>(() => buildColumns(), []);

  const filteredData = useMemo<SaatgutItem[]>(() => {
    if (!Array.isArray(saatgutList?.items)) return [];
    const term = search.trim().toLowerCase();
    if (term.length === 0) return saatgutList.items;
    return saatgutList.items.filter((item: SaatgutItem) =>
      item.name.toLowerCase().includes(term) ||
      item.artikelnummer.toLowerCase().includes(term) ||
      item.sorte.toLowerCase().includes(term) ||
      item.art.toLowerCase().includes(term) ||
      item.zuechter?.toLowerCase().includes(term)
    );
  }, [saatgutList, search]);

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
      title="Saatgut-Verwaltung"
      subtitle="Übersicht aller Saatgut-Arten und -Sorten"
      data={filteredData}
      columns={columns}
      primaryActions={[
        {
          id: 'create-saatgut',
          label: 'Neues Saatgut',
          onClick: (): void => navigate('/agrar/saatgut-stamm'),
        },
      ]}
      overflowActions={[
        {
          id: 'export-saatgut',
          label: 'Export CSV',
          onClick: (): void => {
            // placeholder for export functionality
          },
        },
      ]}
      searchPlaceholder="Saatgut suchen (Name, Artikelnummer, Sorte, Art, Züchter)"
      onSearch={setSearch}
      filterOptions={[
        {
          field: 'art',
          label: 'Art',
          type: 'select',
          options: [
            { value: 'Weizen', label: 'Weizen' },
            { value: 'Gerste', label: 'Gerste' },
            { value: 'Roggen', label: 'Roggen' },
            { value: 'Hafer', label: 'Hafer' },
            { value: 'Mais', label: 'Mais' },
            { value: 'Raps', label: 'Raps' },
          ],
        },
        {
          field: 'bsa_zulassung',
          label: 'BSA-Zulassung',
          type: 'select',
          options: [
            { value: 'true', label: 'Ja' },
            { value: 'false', label: 'Nein' },
          ],
        },
        {
          field: 'eu_zulassung',
          label: 'EU-Zulassung',
          type: 'select',
          options: [
            { value: 'true', label: 'Ja' },
            { value: 'false', label: 'Nein' },
          ],
        },
      ]}
      selectable
      mcpContext={{
        pageDomain: 'agrar',
        currentDocument: 'saatgut',
      }}
    />
  );
};

export default SaatgutListePage;