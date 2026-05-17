import { useAuth } from '@/store/AuthContext'

export default function Header() {
  const { user, logout } = useAuth()
  return (
    <header className="h-14 border-b flex items-center justify-end px-6 bg-background">
      <div className="flex items-center gap-4">
        {user && (
          <span className="text-sm text-muted-foreground">{user.name}</span>
        )}
        <button
          onClick={logout}
          className="text-sm text-destructive hover:underline"
        >
          Sair
        </button>
      </div>
    </header>
  )
}
