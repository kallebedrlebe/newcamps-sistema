import { useState, FormEvent } from 'react'
import { useEmpresas } from '@/hooks/useEmpresa'
import { useDisparaTarefa } from '@/hooks/useTarefa'
import type { Tarefa } from '@/types/tarefa'

export default function DarfPage() {
  const { data: empresas = [] } = useEmpresas(true)
  const [empresaId, setEmpresaId] = useState('')
  const [competencia, setCompetencia] = useState('')
  const [codigo, setCodigo] = useState('')
  const [resultado, setResultado] = useState<Tarefa | null>(null)
  const disparar = useDisparaTarefa('/ecac/darf')

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    const tarefa = await disparar.mutateAsync({
      empresa_id: Number(empresaId),
      competencia,
      codigo_receita: codigo,
    })
    setResultado(tarefa)
  }

  return (
    <div className="max-w-md space-y-4">
      <h1 className="text-xl font-semibold">Emissão de DARF</h1>
      <form onSubmit={handleSubmit} className="space-y-4 rounded-lg border p-6 bg-card">
        <div className="space-y-1">
          <label className="text-sm font-medium">Empresa</label>
          <select
            value={empresaId}
            onChange={e => setEmpresaId(e.target.value)}
            required
            className="w-full px-3 py-2 rounded-md border bg-background text-sm focus:outline-none focus:ring-2 focus:ring-ring"
          >
            <option value="">Selecione...</option>
            {empresas.map(e => <option key={e.id} value={e.id}>{e.razao_social}</option>)}
          </select>
        </div>
        <div className="space-y-1">
          <label className="text-sm font-medium">Competência (YYYY-MM)</label>
          <input
            value={competencia}
            onChange={e => setCompetencia(e.target.value)}
            placeholder="2024-01"
            required
            className="w-full px-3 py-2 rounded-md border bg-background text-sm focus:outline-none focus:ring-2 focus:ring-ring"
          />
        </div>
        <div className="space-y-1">
          <label className="text-sm font-medium">Código da Receita</label>
          <input
            value={codigo}
            onChange={e => setCodigo(e.target.value)}
            required
            className="w-full px-3 py-2 rounded-md border bg-background text-sm focus:outline-none focus:ring-2 focus:ring-ring"
          />
        </div>
        <button
          type="submit"
          disabled={disparar.isPending}
          className="w-full py-2 rounded-md bg-primary text-primary-foreground text-sm font-medium hover:opacity-90 disabled:opacity-50"
        >
          {disparar.isPending ? 'Enviando...' : 'Emitir DARF'}
        </button>
      </form>
      {resultado && (
        <div className="rounded-lg border p-4 bg-muted/30 text-sm">
          Tarefa <strong>#{resultado.id}</strong> criada — status: <strong>{resultado.status}</strong>
        </div>
      )}
    </div>
  )
}
