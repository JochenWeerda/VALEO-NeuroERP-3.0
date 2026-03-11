import { useState } from 'react'
import { clsx } from 'clsx'
import { useNavigate } from 'react-router-dom'
import {
  Calculator,
  Calendar,
  ChevronRight,
  FileText,
  Mail,
  MessageSquare,
  Package,
  Phone,
  Plus,
  Receipt,
  Send,
  ShoppingCart,
  Truck,
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from '@/components/ui/popover'

interface IntentAction {
  id: string
  label: string
  icon: React.ReactNode
  shortcut?: string
  action: () => void
  color?: string
}

interface IntentBarProps {
  customerId: string
  customerName?: string
  customerEmail?: string
  customerPhone?: string
  className?: string
}

export function IntentBar({
  customerId,
  customerEmail,
  customerPhone,
  className,
}: IntentBarProps) {
  const navigate = useNavigate()
  const [quickInput, setQuickInput] = useState('')
  const [showMore, setShowMore] = useState(false)

  const primaryActions: IntentAction[] = [
    {
      id: 'quote',
      label: 'Angebot',
      icon: <FileText className="h-4 w-4" />,
      shortcut: 'A',
      color: 'bg-blue-500 hover:bg-blue-600',
      action: () => navigate(`/sales/angebote/neu?customerId=${customerId}`),
    },
    {
      id: 'order',
      label: 'Auftrag',
      icon: <ShoppingCart className="h-4 w-4" />,
      shortcut: 'B',
      color: 'bg-green-500 hover:bg-green-600',
      action: () => navigate(`/sales/auftraege/neu?customerId=${customerId}`),
    },
    {
      id: 'invoice',
      label: 'Rechnung',
      icon: <Receipt className="h-4 w-4" />,
      shortcut: 'R',
      color: 'bg-purple-500 hover:bg-purple-600',
      action: () => navigate(`/finance/invoices/neu?customerId=${customerId}`),
    },
  ]

  const secondaryActions: IntentAction[] = [
    {
      id: 'delivery',
      label: 'Lieferschein',
      icon: <Truck className="h-4 w-4" />,
      action: () => navigate(`/sales/lieferungen/neu?customerId=${customerId}`),
    },
    {
      id: 'appointment',
      label: 'Termin',
      icon: <Calendar className="h-4 w-4" />,
      action: () => navigate(`/crm/activities/neu?customerId=${customerId}&type=appointment`),
    },
    {
      id: 'task',
      label: 'Aufgabe',
      icon: <MessageSquare className="h-4 w-4" />,
      action: () => navigate(`/crm/activities/neu?customerId=${customerId}&type=task`),
    },
    {
      id: 'article',
      label: 'Artikel zuordnen',
      icon: <Package className="h-4 w-4" />,
      action: () => navigate(`/crm/customers/${customerId}/articles`),
    },
    {
      id: 'calculation',
      label: 'Kalkulation',
      icon: <Calculator className="h-4 w-4" />,
      action: () => navigate(`/sales/kalkulationen/neu?customerId=${customerId}`),
    },
  ]

  const communicationActions: IntentAction[] = [
    {
      id: 'email',
      label: 'E-Mail',
      icon: <Mail className="h-4 w-4" />,
      action: () => {
        if (customerEmail) {
          window.location.href = `mailto:${customerEmail}?subject=Anfrage%20von%20VALEO%20ERP`
        }
      },
    },
    {
      id: 'call',
      label: 'Anrufen',
      icon: <Phone className="h-4 w-4" />,
      action: () => {
        if (customerPhone) {
          window.location.href = `tel:${customerPhone}`
        }
      },
    },
  ]

  const handleQuickAction = () => {
    const input = quickInput.toLowerCase().trim()

    // Parse quick input
    if (input.startsWith('angebot') || input.startsWith('quote')) {
      navigate(`/sales/angebote/neu?customerId=${customerId}`)
    } else if (input.startsWith('auftrag') || input.startsWith('order')) {
      navigate(`/sales/auftraege/neu?customerId=${customerId}`)
    } else if (input.startsWith('rechnung') || input.startsWith('invoice')) {
      navigate(`/finance/invoices/neu?customerId=${customerId}`)
    } else if (input.startsWith('mail') || input.startsWith('email')) {
      if (customerEmail) {
        window.location.href = `mailto:${customerEmail}`
      }
    } else if (input.startsWith('anruf') || input.startsWith('call')) {
      if (customerPhone) {
        window.location.href = `tel:${customerPhone}`
      }
    }

    setQuickInput('')
  }

  return (
    <div
      className={clsx(
        'flex items-center gap-2 p-3 bg-muted/50 rounded-lg border',
        className
      )}
    >
      {/* Quick Input */}
      <div className="flex-1 relative">
        <Input
          placeholder="Schnellaktion eingeben... (z.B. 'Angebot', 'Auftrag')"
          value={quickInput}
          onChange={(e) => setQuickInput(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === 'Enter') {
              handleQuickAction()
            }
          }}
          className="pr-10"
        />
        <Button
          variant="ghost"
          size="icon"
          className="absolute right-1 top-1/2 -translate-y-1/2 h-7 w-7"
          onClick={handleQuickAction}
          disabled={!quickInput}
        >
          <Send className="h-4 w-4" />
        </Button>
      </div>

      {/* Divider */}
      <div className="h-8 w-px bg-border" />

      {/* Primary Actions */}
      <div className="flex items-center gap-1">
        {primaryActions.map((action) => (
          <Button
            key={action.id}
            size="sm"
            className={clsx('gap-1', action.color, 'text-white')}
            onClick={action.action}
            title={action.shortcut ? `${action.label} (${action.shortcut})` : action.label}
          >
            {action.icon}
            <span className="hidden sm:inline">{action.label}</span>
          </Button>
        ))}
      </div>

      {/* Communication */}
      <div className="flex items-center gap-1">
        {communicationActions.map((action) => (
          <Button
            key={action.id}
            variant="outline"
            size="icon"
            className="h-8 w-8"
            onClick={action.action}
            disabled={
              (action.id === 'email' && !customerEmail) ||
              (action.id === 'call' && !customerPhone)
            }
            title={action.label}
          >
            {action.icon}
          </Button>
        ))}
      </div>

      {/* More Actions */}
      <Popover open={showMore} onOpenChange={setShowMore}>
        <PopoverTrigger asChild>
          <Button variant="outline" size="sm" className="gap-1">
            <Plus className="h-4 w-4" />
            <span className="hidden sm:inline">Mehr</span>
            <ChevronRight
              className={clsx('h-4 w-4 transition-transform', showMore && 'rotate-90')}
            />
          </Button>
        </PopoverTrigger>
        <PopoverContent className="w-48 p-1" align="end">
          {secondaryActions.map((action) => (
            <Button
              key={action.id}
              variant="ghost"
              className="w-full justify-start gap-2"
              onClick={() => {
                action.action()
                setShowMore(false)
              }}
            >
              {action.icon}
              {action.label}
            </Button>
          ))}
        </PopoverContent>
      </Popover>
    </div>
  )
}
