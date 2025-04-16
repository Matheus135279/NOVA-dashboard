import { useLocation, Link } from 'react-router-dom'
import { 
  LayoutDashboard, 
  Target, 
  Facebook, 
  FileText, 
  Settings 
} from 'lucide-react'

interface SidebarProps {
  isOpen: boolean
  setIsOpen: (isOpen: boolean) => void
}

const menuItems = [
  { icon: LayoutDashboard, label: 'Dashboard', path: '/' },
  { icon: Target, label: 'Google Ads', path: '/google-ads' },
  { icon: Facebook, label: 'Facebook Ads', path: '/facebook-ads' },
  { icon: FileText, label: 'Relatórios', path: '/reports' },
  { icon: Settings, label: 'Configurações', path: '/settings' }
]

export default function Sidebar({ isOpen, setIsOpen }: SidebarProps) {
  const location = useLocation()

  return (
    <aside className={`
      w-64 h-screen bg-[#2C1A4B] fixed left-0 top-0
      transition-all duration-300 ease-in-out
      ${isOpen ? 'translate-x-0' : '-translate-x-64'}
    `}>
      <div className="p-6">
        {/* Logo */}
        <div className="flex justify-center mb-8">
          <img 
            src="/logo.png" 
            alt="Logo" 
            className="h-12"
          />
        </div>

        {/* Menu Items */}
        <nav className="space-y-2">
          {menuItems.map((item) => {
            const isActive = location.pathname === item.path
            const Icon = item.icon

            return (
              <Link
                key={item.path}
                to={item.path}
                className={`
                  flex items-center gap-3 px-4 py-3 rounded-lg
                  transition-all duration-200
                  ${isActive 
                    ? 'bg-white/10 shadow-lg' 
                    : 'hover:bg-white/5'
                  }
                `}
              >
                <Icon className="w-5 h-5" />
                <span className="text-sm font-medium">
                  {item.label}
                </span>
              </Link>
            )
          })}
        </nav>
      </div>
    </aside>
  )
} 