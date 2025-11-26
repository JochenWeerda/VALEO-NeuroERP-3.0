/**
 * CrudPrintButton Component
 * Button for printing/exporting data (PDF, Excel)
 */

import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Button } from '@/components/ui/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { Download, FileText, FileSpreadsheet, Loader2 } from 'lucide-react';
import { crudPrintService } from '../services/crud-print-service';

export interface CrudPrintButtonProps {
  onPrintPDF?: () => void | Promise<void>;
  onPrintExcel?: () => void | Promise<void>;
  entityType?: string;
  disabled?: boolean;
  isLoading?: boolean;
  // For list printing
  listData?: any[];
  listColumns?: Array<{ header: string; field: string }>;
  // For detail printing
  detailEntity?: any;
  printTitle?: string;
}

export function CrudPrintButton({
  onPrintPDF,
  onPrintExcel,
  entityType = 'Daten',
  disabled = false,
  isLoading = false,
  listData,
  listColumns,
  detailEntity,
  printTitle,
}: CrudPrintButtonProps) {
  const { t } = useTranslation();
  const [isPrinting, setIsPrinting] = useState(false);

  const handlePrintPDF = async () => {
    if (onPrintPDF) {
      setIsPrinting(true);
      try {
        await onPrintPDF();
      } finally {
        setIsPrinting(false);
      }
      return;
    }

    // Default implementation
    if (listData && listColumns) {
      setIsPrinting(true);
      try {
        await crudPrintService.printListAsPDF(listData, listColumns, {
          title: printTitle || `${entityType} Liste`,
          format: 'PDF',
        });
      } catch (error) {
        console.error('Error printing PDF:', error);
        alert(t('crud.print.errorPDF'));
      } finally {
        setIsPrinting(false);
      }
    } else if (detailEntity) {
      setIsPrinting(true);
      try {
        await crudPrintService.printDetailAsPDF(detailEntity, entityType, {
          title: printTitle || `${entityType} Detail`,
          format: 'PDF',
        });
      } catch (error) {
        console.error('Error printing PDF:', error);
        alert(t('crud.print.errorPDF'));
      } finally {
        setIsPrinting(false);
      }
    }
  };

  const handlePrintExcel = async () => {
    if (onPrintExcel) {
      setIsPrinting(true);
      try {
        await onPrintExcel();
      } finally {
        setIsPrinting(false);
      }
      return;
    }

    // Default implementation
    if (listData && listColumns) {
      setIsPrinting(true);
      try {
        await crudPrintService.printListAsExcel(listData, listColumns, {
          title: printTitle || `${entityType} Liste`,
          format: 'EXCEL',
        });
      } catch (error) {
        console.error('Error printing Excel:', error);
        alert(t('crud.print.errorExcel'));
      } finally {
        setIsPrinting(false);
      }
    }
  };

  const hasAnyAction = onPrintPDF || onPrintExcel;

  if (!hasAnyAction) {
    return null;
  }

  if (onPrintPDF && !onPrintExcel) {
      return (
        <Button
          onClick={handlePrintPDF}
          disabled={disabled || isLoading || isPrinting}
          variant="outline"
        >
          {isPrinting ? (
            <>
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              {t('crud.print.exporting')}
            </>
          ) : (
            <>
              <FileText className="mr-2 h-4 w-4" />
              {t('crud.print.exportAsPDF')}
            </>
          )}
        </Button>
      );
  }

  if (onPrintExcel && !onPrintPDF) {
      return (
        <Button
          onClick={handlePrintExcel}
          disabled={disabled || isLoading || isPrinting}
          variant="outline"
        >
          {isPrinting ? (
            <>
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              {t('crud.print.exporting')}
            </>
          ) : (
            <>
              <FileSpreadsheet className="mr-2 h-4 w-4" />
              {t('crud.print.exportAsExcel')}
            </>
          )}
        </Button>
      );
  }

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button
          disabled={disabled || isLoading || isPrinting}
          variant="outline"
        >
          {isPrinting ? (
            <>
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              {t('crud.print.exporting')}
            </>
          ) : (
            <>
              <Download className="mr-2 h-4 w-4" />
              {t('crud.print.export')}
            </>
          )}
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end">
        {onPrintPDF && (
          <DropdownMenuItem onClick={handlePrintPDF} disabled={isPrinting}>
            <FileText className="mr-2 h-4 w-4" />
            {t('crud.print.exportAsPDF')}
          </DropdownMenuItem>
        )}
        {onPrintExcel && (
          <DropdownMenuItem onClick={handlePrintExcel} disabled={isPrinting}>
            <FileSpreadsheet className="mr-2 h-4 w-4" />
            {t('crud.print.exportAsExcel')}
          </DropdownMenuItem>
        )}
      </DropdownMenuContent>
    </DropdownMenu>
  );
}

