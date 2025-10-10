import * as React from "react"
import { Button } from "@/components/ui/button"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"

type Props = {
  domain: string
}

/**
 * ExportButton - Exportiert Belege als CSV/XLSX
 */
export function ExportButton({ domain }: Props): JSX.Element {
  function handleExport(format: "csv" | "xlsx"): void {
    window.open(`/api/export/${domain}?fmt=${format}`, "_blank")
  }

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="outline">📊 Export</Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent>
        <DropdownMenuItem
          onClick={(): void => {
            handleExport("csv")
          }}
        >
          CSV
        </DropdownMenuItem>
        <DropdownMenuItem
          onClick={(): void => {
            handleExport("xlsx")
          }}
        >
          Excel (XLSX)
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  )
}

