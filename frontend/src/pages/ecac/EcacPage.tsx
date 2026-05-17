import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useEmpresas } from '@/hooks/useEmpresa'
import { useTarefas } from '@/hooks/useTarefa'
import DataTable from '@/components/shared/DataTable'
import StatusBadge from '@/components/shared/StatusBadge'
import type { Tarefa, StatusTarefa } from '@/types/tarefa'

const modulos = [
  {
    titulo: 'DCTFWeb — DARF eSocial',
    descricao: 'Acessa a DCTFWeb e emite o DARF das contribuições do eSocial por competência.',
    to: '/ecac/dctfweb/esocial',
    destaque: true,
  },
  {
    titulo: 'Emissão de DARF',
    descricao: 'Emite DARF via SICALC para qualquer código de receita.',
    to: '/ecac/darf',
    destaque: false,
  },
]

export default function EcacPage() {
  const { data: empresas = [] } = useEmpresas(true)
  const [empresaId, setEmpresaId] = useState<number | undefined>()
  const { data: tarefas = [], isLoading } = useTarefas(empresaId)
  const navigate = useNavigate()

  const ecacTarefas = tarefas.filter(t => t.tipo.startsWith('ECAC_'))
  const columns = [
    { header: 'ID', accessor: 'id' as keyof Tarefa },
    { header: 'Tipo', accessor: (t: Tarefa) => tipoLabel(t.tipo) },
    { header: 'Competência', accessor: (t: Tarefa) => t.parametros?.competencia as string ?? '—' },
    {
      header: 'Valor Total',
      accessor: (t: Tarefa) =>
        t.resultado?.valor_total != null
          ? `R$ ${Number(t.resultado.valor_total).toLocaleString('pt-BR', { minimumFractionDigits: 2 })}`
          : '—',
    },
    { header: 'Status', accessor: (t: Tarefa) => <StatusBadge status={t.status as StatusTarefa} /> },
    { header: 'Criado em', accessor: (t: Tarefa) => new Date(t.criado_em).toLocaleString('pt-BR') },
  ]

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-semibold">e-CAC — Receita Federal</h1>
        <p className="text-sm text-muted-foreground mt-1">
          Automação do Centro Virtual de Atendimento da Receita Federal.
        </p>
      </div>

      {/* Cards de módulos */}
      <div className="grid gap-4 sm:grid-cols-2">
        {modulos.map(m => (
          <button
            key={m.to}
            onClick={() => navigate(m.to)}
            className={`rounded-lg border-2 p-5 text-left space-y-1 hover:shadow-sm transition-shadow ${
              m.destaque ? 'border-blue-300 bg-blue-50/40' : 'border-border bg-card'
            }`}
          >
            <div className="flex items-center gap-2">
              <h3 className="font-semibold text-sm">{m.titulo}</h3>
              {m.destaque && (
                <span className="text-[10px] font-medium bg-blue-100 text-blue-700 px-1.5 py-0.5 rounded">
                  PRINCIPAL
                </span>
              )}
            </div>
            <p className="text-xs text-muted-foreground">{m.descricao}</p>
          </button>
        ))}
      </div>

      {/* Histórico de tarefas */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <h2 className="text-sm font-medium">Histórico de tarefas</h2>
          <select
            value={empresaId ?? ''}
            onChange={e => setEmpresaId(e.target.value ? Number(e.target.value) : undefined)}
            className="px-2 py-1 rounded-md border bg-background text-sm focus:outline-none focus:ring-2 focus:ring-ring"
          >
            <option value="">Todas as empresas</option>
            {empresas.map(e => <option key={e.id} value={e.id}>{e.razao_social}</option>)}
          </select>
        </div>
        {isLoading ? (
          <p className="text-sm text-muted-foreground">Carregando...</p>
        ) : (
          <DataTable
            columns={columns}
            data={ecacTarefas}
            keyField="id"
            emptyMessage="Nenhuma tarefa e-CAC encontrada."
          />
        )}
      </div>
    </div>
  )
}

function tipoLabel(tipo: string): string {
  const labels: Record<string, string> = {
    ECAC_DCTFWEB_ESOCIAL: 'DCTFWeb eSocial',
    ECAC_DARF: 'DARF',
    ECAC_DEBITOS: 'Débitos',
    ECAC_PARCELAMENTO: 'Parcelamento',
  }
  return labels[tipo] ?? tipo
}
