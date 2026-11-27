import { useMemo } from 'react'
import documentPermissions from './beleg-permissions.generated.json'
import actionPermissions from './action-permissions.generated.json'
import { useAuth } from '@/hooks/useAuth'
import type { User } from '@/lib/auth'
import type { ScreenDefinition } from '../schema'

/** UI projection of authenticated rights; server dependencies remain authoritative. */
export function getScreenPermissions(screen: ScreenDefinition | undefined, user: User | null): string[] {
  if (!screen || !user) return []
  const scopes = new Set(user.scopes ?? [])
  const roles = new Set(user.roles ?? [])
  const rows = [...(screen.tables ?? []), ...(screen.tabs ?? []).flatMap(tab => tab.tables ?? [])]
    .flatMap(table => table.rowActions ?? [])
  const declared = new Set([...(screen.actions ?? []), ...rows].flatMap(action => action.permission ? [action.permission] : []))
  if (screen.creation) declared.add(screen.creation.permission)
  return [...declared].filter(permission => {
    if (permission.startsWith('belege.')) {
      const screens = documentPermissions.screens as Record<string, Record<string, string[]>>
      return (screens[screen.id]?.[permission] ?? []).some(role => roles.has(role))
    }
    if (permission.startsWith('studio.entity.')) {
      const groups = (actionPermissions.generatedEntities as Record<string, string[][]>)[permission]
      return Boolean(groups?.length && groups.every(group => group.some(role => roles.has(role))))
    }
    const projected = (actionPermissions.screens as Record<string, Record<string, string[][]>>)[screen.id]?.[permission]
    if (projected) return projected.length > 0 && projected.every(group => group.some(role => roles.has(role)))
    if (permission.startsWith('platform:')) return scopes.has(permission)
    if (permission === 'identity:quota:read') return true // Server returns only own allocations.
    if (scopes.has('admin:all') || roles.has('admin')) return true
    if (scopes.has(permission)) return true
    if (permission === 'logistics:read' && scopes.has('logistics:write')) return true
    // Match the canonical lead API's existing role contract, not schema-granted rights.
    if (
      permission.startsWith('crm.lead.')
      || permission.startsWith('crm.contact.')
      || permission.startsWith('crm.betriebsprofil.')
      || permission.startsWith('crm.vertreter.')
    ) {
      return roles.has('CRM_BEARBEITEN') || roles.has('CRM_ADMIN') || roles.has('manager')
    }
    // Agrar Saatgut/Duenger/Rohwarengruppe/Vermehrung Create mirrors SCHREIBEN["AGRAR"] / LAGER for Rohware.
    if (permission.startsWith('agrar.rohwarengruppe.')) {
      return roles.has('LAGER_BEARBEITEN') || roles.has('LAGER_ADMIN') || roles.has('manager')
    }
    if (permission.startsWith('agrar.vermehrungsvertrag.')) {
      return (
        roles.has('AGRAR_BEARBEITEN') || roles.has('AGRAR_ADMIN')
        || roles.has('HARVEST_BEARBEITEN') || roles.has('HARVEST_ADMIN')
        || roles.has('KONTRAKT_BEARBEITEN') || roles.has('KONTRAKT_ADMIN')
        || roles.has('FUTTERMITTEL_BEARBEITEN') || roles.has('FUTTERMITTEL_ADMIN')
        || roles.has('manager')
      )
    }
    if (
      permission.startsWith('agrar.saatgut.')
      || permission.startsWith('agrar.duenger.')
      || permission.startsWith('agrar.sammelabrechnung.')
      || permission.startsWith('agrar.qualitaet_nachtrag.')
      || permission.startsWith('agrar.erntefenster.')
      || permission.startsWith('agrar.milchvieh_crosssell.')
    ) {
      return (
        roles.has('AGRAR_BEARBEITEN') || roles.has('AGRAR_ADMIN')
        || roles.has('HARVEST_BEARBEITEN') || roles.has('HARVEST_ADMIN')
        || roles.has('KONTRAKT_BEARBEITEN') || roles.has('KONTRAKT_ADMIN')
        || roles.has('FUTTERMITTEL_BEARBEITEN') || roles.has('FUTTERMITTEL_ADMIN')
        || roles.has('manager')
      )
    }
    // Mengenzeitraum / Zu-Abschlag mirrors SCHREIBEN["KONTRAKT"].
    if (
      permission.startsWith('kontrakte.mengenzeitraum.')
      || permission.startsWith('kontrakte.zuabschlag.')
    ) {
      return roles.has('KONTRAKT_BEARBEITEN') || roles.has('KONTRAKT_ADMIN') || roles.has('manager')
    }
    // Finance Stamm-Create / Zinsabrechnung mirrors SCHREIBEN["FINANZ"] until projection covers POST.
    if (
      permission.startsWith('finance.bankkonto.')
      || permission.startsWith('finance.kreditor.')
      || permission.startsWith('finance.zinsabrechnung.')
    ) {
      return roles.has('FINANCE_BEARBEITEN') || roles.has('FINANCE_ADMIN') || roles.has('manager')
    }
    // AI-Freigaben: Admin-Ops + Finance (AP-Approval).
    if (permission.startsWith('admin.ai_approvals.')) {
      return (
        roles.has('ADMIN') || roles.has('manager')
        || roles.has('FINANCE_BEARBEITEN') || roles.has('FINANCE_ADMIN')
      )
    }
    // Command Monitor: Admin-Ops Read-Model.
    if (permission.startsWith('admin.command_monitor.')) {
      return roles.has('ADMIN') || roles.has('manager')
    }
    // Admin Suite: Readiness und Setup.
    if (permission.startsWith('admin.admin_suite.')) {
      return roles.has('ADMIN') || roles.has('manager')
    }
    // Agrar-Arbeitsplaetze (Schlagkartei / Milchvieh / Ernte / Settlement).
    if (
      permission.startsWith('agrar.schlagkartei.')
      || permission.startsWith('agrar.milchvieh.')
      || permission.startsWith('agrar.ernte_annahme.')
      || permission.startsWith('agrar.settlement.')
    ) {
      return (
        roles.has('AGRAR_BEARBEITEN') || roles.has('AGRAR_ADMIN') || roles.has('AGRAR_LESEN')
        || roles.has('CRM_BEARBEITEN') || roles.has('CRM_ADMIN')
        || roles.has('manager') || roles.has('ADMIN')
      )
    }
    // Lager Materialfluss.
    if (permission.startsWith('lager.materialfluss.')) {
      return (
        roles.has('LAGER_BEARBEITEN') || roles.has('LAGER_ADMIN') || roles.has('LAGER_LESEN')
        || roles.has('AGRAR_BEARBEITEN') || roles.has('AGRAR_ADMIN')
        || roles.has('manager') || roles.has('ADMIN')
      )
    }
    // Opportunity Create mirrors SCHREIBEN["CRM"] (CRM + SALES write roles).
    if (permission.startsWith('crm.opportunity.')) {
      return (
        roles.has('CRM_BEARBEITEN') || roles.has('CRM_ADMIN')
        || roles.has('SALES_BEARBEITEN') || roles.has('SALES_ADMIN')
        || roles.has('manager')
      )
    }
    // Einkauf Create mirrors SCHREIBEN["EINKAUF"] (Anfrage/Angebot/Avis/AB/Supplier).
    if (
      permission.startsWith('einkauf.anfrage.')
      || permission.startsWith('einkauf.angebot.')
      || permission.startsWith('einkauf.anlieferavis.')
      || permission.startsWith('einkauf.auftragsbestaetigung.')
      || permission.startsWith('einkauf.supplier.')
    ) {
      return roles.has('EINKAUF_BEARBEITEN') || roles.has('EINKAUF_ADMIN') || roles.has('manager')
    }
    // Reklamation Create mirrors SCHREIBEN["QUALITAET"] (Lager/Einkauf/Sales/Agrar/Futtermittel).
    if (permission.startsWith('qualitaet.reklamation.')) {
      return (
        roles.has('LAGER_BEARBEITEN') || roles.has('LAGER_ADMIN')
        || roles.has('EINKAUF_BEARBEITEN') || roles.has('EINKAUF_ADMIN')
        || roles.has('SALES_BEARBEITEN') || roles.has('SALES_ADMIN')
        || roles.has('AGRAR_BEARBEITEN') || roles.has('AGRAR_ADMIN')
        || roles.has('FUTTERMITTEL_BEARBEITEN') || roles.has('FUTTERMITTEL_ADMIN')
        || roles.has('manager')
      )
    }
    // Labor Create mirrors SCHREIBEN["AGRAR"] on POST /qualitaet/labor-auftraege.
    if (permission.startsWith('qualitaet.labor.')) {
      return (
        roles.has('AGRAR_BEARBEITEN') || roles.has('AGRAR_ADMIN')
        || roles.has('HARVEST_BEARBEITEN') || roles.has('HARVEST_ADMIN')
        || roles.has('KONTRAKT_BEARBEITEN') || roles.has('KONTRAKT_ADMIN')
        || roles.has('FUTTERMITTEL_BEARBEITEN') || roles.has('FUTTERMITTEL_ADMIN')
        || roles.has('manager')
      )
    }
    // Service Anfrage Create mirrors SCHREIBEN["FACHLICH"].
    if (permission.startsWith('service.anfrage.')) {
      const fachlich = [
        'SALES', 'CRM', 'EINKAUF', 'LAGER', 'AGRAR', 'HARVEST', 'KONTRAKT',
        'FUTTERMITTEL', 'FINANCE', 'PERSONAL',
      ]
      return fachlich.some(b => roles.has(`${b}_BEARBEITEN`) || roles.has(`${b}_ADMIN`)) || roles.has('manager')
    }
    if (permission.startsWith('personal.mitarbeiter.') || permission.startsWith('personal.schulung.')) {
      return roles.has('PERSONAL_BEARBEITEN') || roles.has('PERSONAL_ADMIN') || roles.has('manager')
    }
    // Betriebsstaetten/Hausbank/Mengeneinheit/Artikel-Stamm Create mirrors SCHREIBEN["STAMMDATEN"].
    if (
      permission.startsWith('stammdaten.betriebsstaette.')
      || permission.startsWith('stammdaten.hausbank.')
      || permission.startsWith('stammdaten.mengeneinheit.')
      || permission.startsWith('stammdaten.stoffstrom.')
      || permission.startsWith('stammdaten.bestandteil.')
      || permission.startsWith('stammdaten.verpackung.')
      || permission.startsWith('stammdaten.indiv_artikel.')
    ) {
      return (
        roles.has('EINKAUF_BEARBEITEN') || roles.has('EINKAUF_ADMIN')
        || roles.has('SALES_BEARBEITEN') || roles.has('SALES_ADMIN')
        || roles.has('LAGER_BEARBEITEN') || roles.has('LAGER_ADMIN')
        || roles.has('manager')
      )
    }
    // Verkauf Kunde Create mirrors SCHREIBEN["CRM"] / customers POST (CRM + SALES).
    if (permission.startsWith('verkauf.kunde.')) {
      return (
        roles.has('CRM_BEARBEITEN') || roles.has('CRM_ADMIN')
        || roles.has('SALES_BEARBEITEN') || roles.has('SALES_ADMIN')
        || roles.has('manager')
      )
    }
    // Preise Individual/Rabatt + Dauerauftrag Create mirrors SCHREIBEN["VERKAUF"] (SALES).
    if (
      permission.startsWith('preise.individualpreis.')
      || permission.startsWith('preise.rabattgruppe.')
      || permission.startsWith('verkauf.dauerauftrag.')
    ) {
      return roles.has('SALES_BEARBEITEN') || roles.has('SALES_ADMIN') || roles.has('manager')
    }
    // Zu-/Abschlaggruppe Create mirrors SCHREIBEN["KONTRAKT"].
    if (permission.startsWith('preise.zuabschlaggruppe.')) {
      return (
        roles.has('KONTRAKT_BEARBEITEN') || roles.has('KONTRAKT_ADMIN')
        || roles.has('AGRAR_BEARBEITEN') || roles.has('AGRAR_ADMIN')
        || roles.has('manager')
      )
    }
    // Rezepturgruppe Create mirrors SCHREIBEN["PRODUKTION"].
    if (permission.startsWith('produktion.rezepturgruppe.')) {
      return (
        roles.has('LAGER_BEARBEITEN') || roles.has('LAGER_ADMIN')
        || roles.has('AGRAR_BEARBEITEN') || roles.has('AGRAR_ADMIN')
        || roles.has('FUTTERMITTEL_BEARBEITEN') || roles.has('FUTTERMITTEL_ADMIN')
        || roles.has('manager')
      )
    }
    // Geschäftsjahr Create mirrors finance_admin (FINANCE_ADMIN / admin).
    if (permission.startsWith('fibu.geschaeftsjahr.')) {
      return roles.has('FINANCE_ADMIN') || roles.has('admin') || roles.has('manager')
    }
    // FiBu Zahlungsmeldung/Auszifferung/Zahlungsformular/Abschluss-Checklist Create mirrors finance_write.
    if (
      permission.startsWith('fibu.zahlungsmeldung.')
      || permission.startsWith('fibu.op_auszifferung.')
      || permission.startsWith('fibu.zahlungsformular.')
      || permission.startsWith('fibu.abschluss_checklist.')
    ) {
      return roles.has('FINANCE_BEARBEITEN') || roles.has('FINANCE_ADMIN') || roles.has('manager')
    }
    // Massebilanz Create mirrors SCHREIBEN["AGRAR"]; PIV mirrors SCHREIBEN["LAGER"].
    if (permission.startsWith('lager.massebilanz.')) {
      return (
        roles.has('AGRAR_BEARBEITEN') || roles.has('AGRAR_ADMIN')
        || roles.has('HARVEST_BEARBEITEN') || roles.has('HARVEST_ADMIN')
        || roles.has('KONTRAKT_BEARBEITEN') || roles.has('KONTRAKT_ADMIN')
        || roles.has('FUTTERMITTEL_BEARBEITEN') || roles.has('FUTTERMITTEL_ADMIN')
        || roles.has('manager')
      )
    }
    if (permission.startsWith('lager.piv.')) {
      return roles.has('LAGER_BEARBEITEN') || roles.has('LAGER_ADMIN') || roles.has('manager')
    }
    // Field-Service Create mirrors SCHREIBEN["AGRAR"].
    if (permission.startsWith('agribusiness.field_service.')) {
      return (
        roles.has('AGRAR_BEARBEITEN') || roles.has('AGRAR_ADMIN')
        || roles.has('HARVEST_BEARBEITEN') || roles.has('HARVEST_ADMIN')
        || roles.has('KONTRAKT_BEARBEITEN') || roles.has('KONTRAKT_ADMIN')
        || roles.has('FUTTERMITTEL_BEARBEITEN') || roles.has('FUTTERMITTEL_ADMIN')
        || roles.has('manager')
      )
    }
    return false
  })
}

export function useScreenPermissions(screen: ScreenDefinition | undefined, requested?: string[]): string[] {
  const { user } = useAuth()
  return useMemo(() => {
    const granted = getScreenPermissions(screen, user)
    return requested ? granted.filter(permission => requested.includes(permission)) : granted
  }, [screen, user, requested])
}
