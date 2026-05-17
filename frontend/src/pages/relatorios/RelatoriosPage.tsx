import { useState } from 'react'
import { useTarefas } from '@/hooks/useTarefa'
import DataTable from '@/components/shared/DataTable'
import StatusBadge from '@/components/shared/StatusBadge'
import type { Tarefa, StatusTarefa } from '@/types/tarefa'
import api from '@/lib/api'

export default function RelatoriosPage() {
  const { data: tarefas = [], isLoading } = useTarefas(undefined, 'CONCLUIDA')
  const [baixando, setBaixando] = useState<number | null>(null)

  const baixarPdf = async (tarefaId: number) => {
    setBaixando(tarefaId)
    try {
      const resp = await api.get(`/relatorios/${tarefaId}/pdf`, { responseType: 'blob' })
      const url = URL.createObjectURL(resp.data)
      const a = document.createElement('a')
      a.href = url
      a.download = `tarefa_${tarefaId}.pdf`
      a.click()
      URL.revokeObjectURL(url)
    } finally {
      setBaixando(null)
    }
  }

  const columns = [
    { header: 'ID', accessor: 'id' as keyof Tarefa },
    { header: 'Tipo', accessor: 'tipo' as keyof Tarefa },
    { header: 'Status', accessor: (t: Tarefa) => <StatusBadge status={t.status as StatusTarefa} /> },
    { header: 'Concluída em', accessor: (t: Tarefa) => new Date(t.atualizado_em).toLocaleString('pt-BR') },
    {
      header: '',
      accessor: (t: Tarefa) => (
        <button
          onClick={() => baixarPdf(t.id)}
          disabled={baixando === t.id}
          className="text-primary text-xs hover:underline disabled:opacity-50"
        >
          {baixando === t.id ? 'Baixando...' : 'PDF'}
        </button>
      ),
    },
  ]

  return (
    <div className="space-y-4">
      <h1 className="text-xl font-semibold">Relatórios</h1>
      <p className="text-sm text-muted-foreground">Tarefas concluídas disponíveis para download em PDF.</p>
      {isLoading ? (
        <p className="text-sm text-muted-foreground">Carregando...</p>
      ) : (
        <DataTable columns={columns} data={tarefas} keyField="id" emptyMessage="Nenhum relatório disponível." />
      )}
    </div>
  )
}
