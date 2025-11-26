/**
 * Advanced Filters Component
 * Erweiterte Filter-Optionen für Listen
 */

import { useState } from 'react'
import { useTranslation } from 'react-i18next'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Calendar } from '@/components/ui/calendar'
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover'
import { CalendarIcon, Filter, X } from 'lucide-react'
import { format } from 'date-fns'
import { de } from 'date-fns/locale'

export interface FilterConfig {
  key: string
  label: string
  type: 'text' | 'select' | 'date' | 'dateRange' | 'number' | 'boolean'
  options?: Array<{ value: string; label: string }>
}

export interface AdvancedFiltersProps {
  filters: FilterConfig[]
  values: Record<string, any>
  onChange: (values: Record<string, any>) => void
  onReset: () => void
}

export function AdvancedFilters({ filters, values, onChange, onReset }: AdvancedFiltersProps) {
  const { t } = useTranslation()
  const [isOpen, setIsOpen] = useState(false)

  const handleChange = (key: string, value: any) => {
    onChange({ ...values, [key]: value })
  }

  const handleRemove = (key: string) => {
    const newValues = { ...values }
    delete newValues[key]
    onChange(newValues)
  }

  const activeFiltersCount = Object.keys(values).filter(key => values[key] !== null && values[key] !== undefined && values[key] !== '').length

  return (
    <Popover open={isOpen} onOpenChange={setIsOpen}>
      <PopoverTrigger asChild>
        <Button variant="outline" size="sm">
          <Filter className="h-4 w-4 mr-2" />
          {t('crud.actions.filter')}
          {activeFiltersCount > 0 && (
            <span className="ml-2 bg-primary text-primary-foreground rounded-full px-2 py-0.5 text-xs">
              {activeFiltersCount}
            </span>
          )}
        </Button>
      </PopoverTrigger>
      <PopoverContent className="w-96" align="start">
        <Card>
          <CardHeader className="pb-3">
            <div className="flex items-center justify-between">
              <CardTitle className="text-lg">{t('crud.list.searchAndFilter')}</CardTitle>
              {activeFiltersCount > 0 && (
                <Button variant="ghost" size="sm" onClick={onReset}>
                  <X className="h-4 w-4 mr-1" />
                  {t('common.reset')}
                </Button>
              )}
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            {filters.map((filter) => {
              const value = values[filter.key]
              
              return (
                <div key={filter.key} className="space-y-2">
                  <label className="text-sm font-medium">{filter.label}</label>
                  
                  {filter.type === 'text' && (
                    <Input
                      value={value || ''}
                      onChange={(e) => handleChange(filter.key, e.target.value)}
                      placeholder={t('crud.list.searchPlaceholder')}
                    />
                  )}
                  
                  {filter.type === 'select' && filter.options && (
                    <Select value={value || ''} onValueChange={(val) => handleChange(filter.key, val)}>
                      <SelectTrigger>
                        <SelectValue placeholder={t('common.optional')} />
                      </SelectTrigger>
                      <SelectContent>
                        {filter.options.map((option) => (
                          <SelectItem key={option.value} value={option.value}>
                            {option.label}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  )}
                  
                  {filter.type === 'date' && (
                    <Popover>
                      <PopoverTrigger asChild>
                        <Button variant="outline" className="w-full justify-start text-left font-normal">
                          <CalendarIcon className="mr-2 h-4 w-4" />
                          {value ? format(new Date(value), 'PPP', { locale: de }) : t('common.optional')}
                        </Button>
                      </PopoverTrigger>
                      <PopoverContent className="w-auto p-0">
                        <Calendar
                          mode="single"
                          selected={value ? new Date(value) : undefined}
                          onSelect={(date) => handleChange(filter.key, date?.toISOString().split('T')[0])}
                          locale={de}
                        />
                      </PopoverContent>
                    </Popover>
                  )}
                  
                  {filter.type === 'number' && (
                    <Input
                      type="number"
                      value={value || ''}
                      onChange={(e) => handleChange(filter.key, e.target.value ? Number(e.target.value) : null)}
                      placeholder={t('common.optional')}
                    />
                  )}
                  
                  {value && (
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleRemove(filter.key)}
                      className="h-6 px-2"
                    >
                      <X className="h-3 w-3" />
                    </Button>
                  )}
                </div>
              )
            })}
            
            <div className="flex justify-end gap-2 pt-2">
              <Button variant="outline" size="sm" onClick={() => setIsOpen(false)}>
                {t('common.close')}
              </Button>
              <Button size="sm" onClick={() => setIsOpen(false)}>
                {t('common.apply')}
              </Button>
            </div>
          </CardContent>
        </Card>
      </PopoverContent>
    </Popover>
  )
}

