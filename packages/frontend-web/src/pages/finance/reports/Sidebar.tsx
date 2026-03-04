import type { JSX } from 'react'
import { BarChart3, BookOpenText, BriefcaseBusiness, Landmark, TrendingUp } from 'lucide-react'
import styles from '../reports.module.css'

const navItems = [
  { label: 'Finanzübersicht', icon: Landmark },
  { label: 'GuV Deep Dive', icon: TrendingUp },
  { label: 'Bilanzstruktur', icon: BarChart3 },
  { label: 'Journal', icon: BookOpenText },
  { label: 'Export-Zentrum', icon: BriefcaseBusiness },
]

export function Sidebar(): JSX.Element {
  return (
    <aside className={styles.sidebar}>
      <div className={styles.logoWrap}>
        <img className={styles.logoImage} src="/branding/valeo-erp-logo.png" alt="VALEO ERP Logo" />
        <p className={styles.logoSubline}>NeuroERP 3.0 · FIBU Suite</p>
      </div>

      <nav className={styles.sidebarNav} aria-label="Dashboard Navigation">
        {navItems.map((item, index) => {
          const Icon = item.icon
          return (
            <button
              key={item.label}
              type="button"
              className={`${styles.navItem} ${index === 0 ? styles.navItemActive : ''}`}
            >
              <Icon size={16} />
              <span>{item.label}</span>
            </button>
          )
        })}
      </nav>
    </aside>
  )
}
