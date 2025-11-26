/**
 * CrudAuditTrailPanel Component
 * Displays audit trail for an entity
 */

import React from 'react';
import { useTranslation } from 'react-i18next';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Badge } from '@/components/ui/badge';
import { format } from 'date-fns';
import { de } from 'date-fns/locale';

export interface ChangeLog {
  id: string;
  action: 'CREATE' | 'UPDATE' | 'DELETE' | 'CANCEL' | 'AMEND' | 'RESTORE';
  reason?: string;
  userId: string;
  userName?: string;
  timestamp: Date | string;
  changedFields?: string[];
  oldValue?: Record<string, any>;
  newValue?: Record<string, any>;
}

export interface CrudAuditTrailPanelProps {
  entityType: string;
  entityId: string;
  changeLogs?: ChangeLog[];
  isLoading?: boolean;
}

const actionColors: Record<string, string> = {
  CREATE: 'bg-green-100 text-green-800',
  UPDATE: 'bg-blue-100 text-blue-800',
  DELETE: 'bg-red-100 text-red-800',
  CANCEL: 'bg-orange-100 text-orange-800',
  AMEND: 'bg-purple-100 text-purple-800',
  RESTORE: 'bg-gray-100 text-gray-800',
};

// Action labels will be loaded from i18n

export function CrudAuditTrailPanel({
  entityType,
  entityId,
  changeLogs = [],
  isLoading = false,
}: CrudAuditTrailPanelProps) {
  const { t } = useTranslation();

  const getActionLabel = (action: string): string => {
    return t(`crud.audit.actions.${action.toLowerCase()}`, { defaultValue: action });
  };

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>{t('crud.audit.title')}</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-muted-foreground">{t('crud.audit.loading')}</p>
        </CardContent>
      </Card>
    );
  }

  if (changeLogs.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>{t('crud.audit.title')}</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-muted-foreground">
            {t('crud.audit.noChanges')}
          </p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>{t('crud.audit.title')}</CardTitle>
      </CardHeader>
      <CardContent>
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>{t('crud.audit.timestamp')}</TableHead>
              <TableHead>{t('crud.audit.action')}</TableHead>
              <TableHead>{t('crud.audit.user')}</TableHead>
              <TableHead>{t('crud.audit.changedFields')}</TableHead>
              <TableHead>{t('crud.audit.reason')}</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {changeLogs.map((log) => {
              const timestamp = typeof log.timestamp === 'string'
                ? new Date(log.timestamp)
                : log.timestamp;

              return (
                <TableRow key={log.id}>
                  <TableCell className="font-mono text-sm">
                    {format(timestamp, 'dd.MM.yyyy HH:mm:ss', { locale: de })}
                  </TableCell>
                  <TableCell>
                    <Badge
                      className={actionColors[log.action] || 'bg-gray-100 text-gray-800'}
                    >
                      {getActionLabel(log.action)}
                    </Badge>
                  </TableCell>
                  <TableCell>
                    {log.userName || log.userId}
                  </TableCell>
                  <TableCell>
                    {log.changedFields && log.changedFields.length > 0 ? (
                      <div className="flex flex-wrap gap-1">
                        {log.changedFields.map((field) => (
                          <Badge
                            key={field}
                            variant="outline"
                            className="text-xs"
                          >
                            {field}
                          </Badge>
                        ))}
                      </div>
                    ) : (
                      <span className="text-muted-foreground">-</span>
                    )}
                  </TableCell>
                  <TableCell>
                    {log.reason ? (
                      <span className="text-sm">{log.reason}</span>
                    ) : (
                      <span className="text-muted-foreground">-</span>
                    )}
                  </TableCell>
                </TableRow>
              );
            })}
          </TableBody>
        </Table>
      </CardContent>
    </Card>
  );
}

