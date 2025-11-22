/**
 * CRUD Print Service
 * Service for printing/exporting CRUD data
 */

export interface PrintOptions {
  title?: string;
  format: 'PDF' | 'EXCEL';
  includeHeaders?: boolean;
}

export class CrudPrintService {
  /**
   * Print list data as PDF
   */
  async printListAsPDF(
    data: any[],
    columns: Array<{ header: string; field: string }>,
    options?: PrintOptions
  ): Promise<void> {
    try {
      const response = await fetch('/api/print/pdf', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          data,
          columns,
          title: options?.title || 'Liste',
          format: 'PDF',
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to generate PDF');
      }

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${options?.title || 'export'}.pdf`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Error printing PDF:', error);
      throw error;
    }
  }

  /**
   * Print list data as Excel
   */
  async printListAsExcel(
    data: any[],
    columns: Array<{ header: string; field: string }>,
    options?: PrintOptions
  ): Promise<void> {
    try {
      const response = await fetch('/api/print/excel', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          data,
          columns,
          title: options?.title || 'Liste',
          format: 'EXCEL',
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to generate Excel');
      }

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${options?.title || 'export'}.xlsx`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Error printing Excel:', error);
      throw error;
    }
  }

  /**
   * Print detail as PDF
   */
  async printDetailAsPDF(
    entity: any,
    entityType: string,
    options?: PrintOptions
  ): Promise<void> {
    try {
      const response = await fetch('/api/print/pdf/detail', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          entity,
          entityType,
          title: options?.title || `${entityType} Detail`,
          format: 'PDF',
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to generate PDF');
      }

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${options?.title || 'detail'}.pdf`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Error printing PDF:', error);
      throw error;
    }
  }
}

// Export singleton instance
export const crudPrintService = new CrudPrintService();

