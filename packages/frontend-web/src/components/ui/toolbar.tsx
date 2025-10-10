import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { Search, Sparkles } from "lucide-react"

export function Toolbar({ onSearch, onCopilot }: { onSearch?: (v: string)=>void; onCopilot?: ()=>void }): JSX.Element {
  return (
    <div className="flex gap-2 mb-4">
      <div className="relative flex-1">
        <Search className="absolute left-2 top-2.5 h-4 w-4 opacity-50" />
        <Input placeholder="Search..." onChange={(e)=>onSearch?.(e.target.value)} className="pl-8" />
      </div>
      <Button variant="outline" onClick={onCopilot}>
        <Sparkles className="h-4 w-4 mr-1" /> Ask VALEO
      </Button>
    </div>
  )
}