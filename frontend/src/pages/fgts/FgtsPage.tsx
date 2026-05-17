import { useState } from 'react'
import { useEmpresas } from '@/hooks/useEmpresa'
import { useTarefas, useDisparaTarefa } from '@/hooks/useTarefa'
import DataTable from '@/components/shared/DataTable'
import StatusBadge from '@/components/shared/StatusBadge'
import type { Tarefa, StatusTarefa } from '@/types/tarefa'

export default function FgtsPage() {
  const { data: empresas = [] } = useEmpresas(true)
  const [empresaId, setEmpresaId] = useState<number | undefined>()
  const { data: tarefas = [], isLoading } = useTarefas(empresaId)
  const dispararSaldo = useDisparaTarefa('/fgts/saldo')
  const dispararExtrato = useDisparaTarefa('/fgts/extrato')

  const fgtsTarefas = tarefas.filter(t => t.tipo.startsWith('FGTS_'))
  const columns = [
    { header: 'ID', accessor: 'id' as keyof Tarefa },
    { header: 'Tipo', accessor: 'tipo' as keyof Tarefa },
    { header: 'Status', accessor: (t: Tarefa) => <StatusBadge status={t.status as StatusTarefa} /> },
    { header: 'Criado em', accessor: (t: Tarefa) => new Date(t.criado_em).toLocaleString('pt-BR') },
  ]

  return (
    <div className="space-y-4">
      <h1 className="text-xl font-semibold">FGTS</h1>
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
          disabled={!empresaId || dispararSaldo.isPending}
          onClick={() => empresaId && dispararSaldo.mutate({ empresa_id: empresaId })}
          className="px-3 py-2 bg-primary text-primary-foreground text-sm rounded-md hover:opacity-90 disabled:opacity-50"
        >
          Consultar Saldo
        </button>
        <button
          disabled={!empresaId || dispararExtrato.isPending}
          onClick={() => empresaId && dispararExtrato.mutate({ empresa_id: empresaId })}
          className="px-3 py-2 bg-secondary text-secondary-foreground text-sm rounded-md hover:opacity-90 disabled:opacity-50"
        >
          Obter Extrato
        </button>
      </div>
      {isLoading ? (
        <p className="text-sm text-muted-foreground">Carregando...</p>
      ) : (
        <DataTable columns={columns} data={fgtsTarefas} keyField="id" emptyMessage="Nenhuma tarefa FGTS." />
      )}
    </div>
  )
}
