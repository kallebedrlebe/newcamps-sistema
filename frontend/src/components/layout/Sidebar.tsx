import { NavLink } from 'react-router-dom'
import { cn } from '@/lib/utils'

const nav = [
  { label: 'Dashboard', to: '/dashboard' },
  { label: 'Empresas', to: '/empresas' },
  { label: 'e-CAC', to: '/ecac' },
  { label: 'FGTS', to: '/fgts' },
  { label: 'TRON', to: '/tron' },
  { label: 'Relatórios', to: '/relatorios' },
]

export default function Sidebar() {
  return (
    <aside className="w-56 border-r bg-card flex flex-col">
      <div className="h-14 flex items-center px-4 border-b">
        <span className="font-bold text-sm tracking-tight">NewCamps Sistema</span>
      </div>
      <nav className="flex-1 py-2">
        {nav.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            className={({ isActive }) =>
              cn(
                'flex items-center px-4 py-2 text-sm transition-colors',
                isActive
                  ? 'bg-primary/10 text-primary font-medium'
                  : 'text-muted-foreground hover:bg-accent hover:text-accent-foreground',
              )
            }
          >
            {item.label}
          </NavLink>
        ))}
      </nav>
    </aside>
  )
}
