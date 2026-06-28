/**
 * Advanced Filters Component
 * Erweiterte Filter-Optionen für Listen
 */

import { useState } from 'react'
import { useTranslation } from 'react-i18next'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { NativeSelect } from '@/components/ui/native-select'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover'
import { Filter, X } from 'lucide-react'

export interface FilterConfig {
  key: string
  label: string
  type: 'text' | 'select' | 'date' | 'dateRange' | 'number' | 'boolean'
  options?: Array<{ value: string; label: string }>
}

export interface AdvancedFiltersProps {
  filters: FilterConfig[]
  values: Record<string, unknown>
  onChange: (values: Record<string, unknown>) => void
  onReset: () => void
}

export function AdvancedFilters({ filters, values, onChange, onReset }: AdvancedFiltersProps) {
  const { t } = useTranslation()
  const [isOpen, setIsOpen] = useState(false)

  const handleChange = (key: string, value: unknown) => {
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
            {filters.map((filter, filterIndex) => {
              const value = values[filter.key]
              
              return (
                <div key={`${filter.key}-${filterIndex}`} className="space-y-2">
                  <label className="text-sm font-medium">{filter.label}</label>
                  
                  {filter.type === 'text' && (
                    <Input
                      value={value || ''}
                      onChange={(e) => handleChange(filter.key, e.target.value)}
                      placeholder={t('crud.list.searchPlaceholder')}
                    />
                  )}
                  
                  {filter.type === 'select' && filter.options && (
                    <NativeSelect
                      value={value || ''}
                      onValueChange={(val) => handleChange(filter.key, val)}
                      options={filter.options}
                      placeholder={t('common.optional')}
                    />
                  )}
                  
                  {filter.type === 'date' && (
                    <Input
                      type="date"
                      value={value || ''}
                      onChange={(e) => handleChange(filter.key, e.target.value || null)}
                    />
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

