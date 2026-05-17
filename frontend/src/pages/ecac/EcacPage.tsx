import { useState } from 'react'
import { useEmpresas } from '@/hooks/useEmpresa'
import { useTarefas, useDisparaTarefa } from '@/hooks/useTarefa'
import DataTable from '@/components/shared/DataTable'
import StatusBadge from '@/components/shared/StatusBadge'
import type { Tarefa, StatusTarefa } from '@/types/tarefa'

export default function EcacPage() {
  const { data: empresas = [] } = useEmpresas(true)
  const [empresaId, setEmpresaId] = useState<number | undefined>()
  const { data: tarefas = [], isLoading } = useTarefas(empresaId)
  const dispararDebitos = useDisparaTarefa('/ecac/debitos')

  const ecacTarefas = tarefas.filter(t => t.tipo.startsWith('ECAC_'))
  const columns = [
    { header: 'ID', accessor: 'id' as keyof Tarefa },
    { header: 'Tipo', accessor: 'tipo' as keyof Tarefa },
    { header: 'Status', accessor: (t: Tarefa) => <StatusBadge status={t.status as StatusTarefa} /> },
    { header: 'Criado em', accessor: (t: Tarefa) => new Date(t.criado_em).toLocaleString('pt-BR') },
  ]

  return (
    <div className="space-y-4">
      <h1 className="text-xl font-semibold">e-CAC — Receita Federal</h1>
      <div className="flex items-center gap-3">
        <select
          value={empresaId ?? ''}
          onChange={e => setEmpresaId(e.target.value ? Number(e.target.value) : undefined)}
          className="px-3 py-2 rounded-md border bg-background text-sm focus:outline-none focus:ring-2 focus:ring-ring"
        >
          <option value="">Todas as empresas</option>
          {empresas.map(e => (
            <option key={e.id} value={e.id}>{e.razao_social}</option>
          ))}
        </select>
        <button
          disabled={!empresaId || dispararDebitos.isPending}
          onClick={() => empresaId && dispararDebitos.mutate({ empresa_id: empresaId })}
          className="px-3 py-2 bg-primary text-primary-foreground text-sm rounded-md hover:opacity-90 disabled:opacity-50"
        >
          Consultar Débitos
        </button>
      </div>
      {isLoading ? (
        <p className="text-sm text-muted-foreground">Carregando tarefas...</p>
      ) : (
        <DataTable columns={columns} data={ecacTarefas} keyField="id" emptyMessage="Nenhuma tarefa e-CAC encontrada." />
      )}
    </div>
  )
}
