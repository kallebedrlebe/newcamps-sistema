import { useState } from 'react'
import { useEmpresas } from '@/hooks/useEmpresa'
import { useTarefas, useDisparaTarefa } from '@/hooks/useTarefa'
import DataTable from '@/components/shared/DataTable'
import StatusBadge from '@/components/shared/StatusBadge'
import type { Tarefa, StatusTarefa } from '@/types/tarefa'

export default function TronPage() {
  const { data: empresas = [] } = useEmpresas(true)
  const [empresaId, setEmpresaId] = useState<number | undefined>()
  const { data: tarefas = [], isLoading } = useTarefas(empresaId)
  const processar = useDisparaTarefa('/tron/processar')
  const relatorio = useDisparaTarefa('/tron/relatorio')

  const tronTarefas = tarefas.filter(t => t.tipo.startsWith('TRON_'))
  const columns = [
    { header: 'ID', accessor: 'id' as keyof Tarefa },
    { header: 'Tipo', accessor: 'tipo' as keyof Tarefa },
    { header: 'Status', accessor: (t: Tarefa) => <StatusBadge status={t.status as StatusTarefa} /> },
    { header: 'Criado em', accessor: (t: Tarefa) => new Date(t.criado_em).toLocaleString('pt-BR') },
  ]

  return (
    <div className="space-y-4">
      <h1 className="text-xl font-semibold">TRON</h1>
      <div className="flex items-center gap-3 flex-wrap">
        <select
          value={empresaId ?? ''}
          onChange={e => setEmpresaId(e.target.value ? Number(e.target.value) : undefined)}
          className="px-3 py-2 rounded-md border bg-background text-sm focus:outline-none focus:ring-2 focus:ring-ring"
        >
          <option value="">Selecione empresa</option>
          {empresas.map(e => <option key={e.id} value={e.id}>{e.razao_social}</option>)}
        </select>
        <button
          disabled={!empresaId || processar.isPending}
          onClick={() => empresaId && processar.mutate({ empresa_id: empresaId })}
          className="px-3 py-2 bg-primary text-primary-foreground text-sm rounded-md hover:opacity-90 disabled:opacity-50"
        >
          Processar
        </button>
        <button
          disabled={!empresaId || relatorio.isPending}
          onClick={() => empresaId && relatorio.mutate({ empresa_id: empresaId })}
          className="px-3 py-2 bg-secondary text-secondary-foreground text-sm rounded-md hover:opacity-90 disabled:opacity-50"
        >
          Gerar Relatório
        </button>
      </div>
      {isLoading ? (
        <p className="text-sm text-muted-foreground">Carregando...</p>
      ) : (
        <DataTable columns={columns} data={tronTarefas} keyField="id" emptyMessage="Nenhuma tarefa TRON." />
      )}
    </div>
  )
}
