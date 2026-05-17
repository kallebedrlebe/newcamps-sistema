import { useNavigate } from 'react-router-dom'
import { useAuth } from '@/store/AuthContext'
import { useEmpresas } from '@/hooks/useEmpresa'
import { useTarefas } from '@/hooks/useTarefa'

const modules = [
  { title: 'e-CAC', description: 'Automação Receita Federal', to: '/ecac', color: 'border-blue-200' },
  { title: 'FGTS', description: 'Fundo de Garantia', to: '/fgts', color: 'border-green-200' },
  { title: 'TRON', description: 'Processamento TRON', to: '/tron', color: 'border-purple-200' },
  { title: 'Empresas', description: 'Gerenciar clientes', to: '/empresas', color: 'border-orange-200' },
  { title: 'Relatórios', description: 'Download de PDFs', to: '/relatorios', color: 'border-yellow-200' },
]

export default function DashboardPage() {
  const { user } = useAuth()
  const navigate = useNavigate()
  const { data: empresas = [] } = useEmpresas()
  const { data: tarefas = [] } = useTarefas()

  const pendentes = tarefas.filter(t => t.status === 'PENDENTE' || t.status === 'EM_EXECUCAO').length
  const erros = tarefas.filter(t => t.status === 'ERRO').length

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-semibold">Olá, {user?.name ?? 'usuário'}</h1>
        <p className="text-sm text-muted-foreground mt-1">Painel de controle — NewCamps Sistema</p>
      </div>

      <div className="grid gap-4 sm:grid-cols-3">
        <div className="rounded-lg border bg-card p-4 space-y-1">
          <p className="text-xs text-muted-foreground uppercase tracking-wide">Empresas ativas</p>
          <p className="text-2xl font-bold">{empresas.filter(e => e.ativa).length}</p>
        </div>
        <div className="rounded-lg border bg-card p-4 space-y-1">
          <p className="text-xs text-muted-foreground uppercase tracking-wide">Tarefas em execução</p>
          <p className="text-2xl font-bold">{pendentes}</p>
        </div>
        <div className="rounded-lg border bg-card p-4 space-y-1">
          <p className="text-xs text-muted-foreground uppercase tracking-wide">Erros recentes</p>
          <p className="text-2xl font-bold text-destructive">{erros}</p>
        </div>
      </div>

      <div>
        <h2 className="text-sm font-medium text-muted-foreground mb-3 uppercase tracking-wide">Módulos</h2>
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {modules.map((mod) => (
            <button
              key={mod.to}
              onClick={() => navigate(mod.to)}
              className={`rounded-lg border-2 ${mod.color} bg-card p-6 space-y-1 hover:shadow-sm transition-shadow text-left`}
            >
              <h3 className="font-semibold">{mod.title}</h3>
              <p className="text-sm text-muted-foreground">{mod.description}</p>
            </button>
          ))}
        </div>
      </div>
    </div>
  )
}
