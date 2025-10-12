import { Button } from "@/components/ui/button"

type Props = {
  domain: string
  number: string
}

/**
 * PrintButton - Öffnet PDF-Druck in neuem Tab
 */
export default function PrintButton({ domain, number }: Props): JSX.Element {
  function handlePrint(): void {
    window.open(`/api/documents/${domain}/${number}/print`, "_blank")
  }

  return (
    <Button variant="secondary" onClick={handlePrint}>
      📄 PDF drucken
    </Button>
  )
}

