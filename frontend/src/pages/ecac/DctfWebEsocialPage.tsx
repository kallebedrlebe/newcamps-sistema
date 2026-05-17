import { useState, FormEvent, useEffect } from 'react'
import { useEmpresas } from '@/hooks/useEmpresa'
import { useTarefa } from '@/hooks/useTarefa'
import StatusBadge from '@/components/shared/StatusBadge'
import type { StatusTarefa } from '@/types/tarefa'
import api from '@/lib/api'

interface DarfResultado {
  codigo_receita: string
  valor_principal: number
  valor_multa: number
  valor_juros: number
  valor_total: number
  data_vencimento: string
  nosso_numero: string
  codigo_barras: string
  competencia: string
  cnpj: string
  pdf_url?: string
}

export default function DctfWebEsocialPage() {
  const { data: empresas = [] } = useEmpresas(true)
  const [empresaId, setEmpresaId] = useState('')
  const [competencia, setCompetencia] = useState('')
  const [codigoMfa, setCodigoMfa] = useState('')
  const [mostrarMfa, setMostrarMfa] = useState(false)
  const [tarefaId, setTarefaId] = useState<number | null>(null)
  const [enviando, setEnviando] = useState(false)
  const [erro, setErro] = useState('')

  // Polling automático enquanto a tarefa está em execução
  const { data: tarefa } = useTarefa(tarefaId ?? 0)
  const resultado = tarefa?.resultado as DarfResultado | null | undefined

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    setErro('')
    setEnviando(true)
    try {
      const { data } = await api.post('/ecac/dctfweb/esocial', {
        empresa_id: Number(empresaId),
        competencia,
        codigo_mfa: codigoMfa || null,
      })
      setTarefaId(data.id)
    } catch (err: any) {
      const detail = err.response?.data?.detail
      setErro(typeof detail === 'string' ? detail : 'Erro ao iniciar a tarefa.')
    } finally {
      setEnviando(false)
    }
  }

  const handleNovaConsulta = () => {
    setTarefaId(null)
    setErro('')
  }

  return (
    <div className="max-w-xl space-y-6">
      <div>
        <h1 className="text-xl font-semibold">DCTFWeb — DARF eSocial</h1>
        <p className="text-sm text-muted-foreground mt-1">
          Acessa o e-CAC, abre a DCTFWeb e emite o DARF das contribuições do eSocial para a competência informada.
        </p>
      </div>

      {/* Formulário */}
      {!tarefaId && (
        <form onSubmit={handleSubmit} className="rounded-lg border bg-card p-6 space-y-4">
          {/* Empresa */}
          <div className="space-y-1">
            <label className="text-sm font-medium">Empresa</label>
            <select
              value={empresaId}
              onChange={e => setEmpresaId(e.target.value)}
              required
              className="w-full px-3 py-2 rounded-md border bg-background text-sm focus:outline-none focus:ring-2 focus:ring-ring"
            >
              <option value="">Selecione a empresa...</option>
              {empresas.map(e => (
                <option key={e.id} value={e.id}>
                  {e.razao_social} — {e.cnpj.replace(/(\d{2})(\d{3})(\d{3})(\d{4})(\d{2})/, '$1.$2.$3/$4-$5')}
                </option>
              ))}
            </select>
            <p className="text-xs text-muted-foreground">
              As credenciais gov.br devem estar cadastradas nas configurações da empresa.
            </p>
          </div>

          {/* Competência */}
          <div className="space-y-1">
            <label className="text-sm font-medium">Competência</label>
            <input
              value={competencia}
              onChange={e => setCompetencia(e.target.value)}
              placeholder="MM/AAAA — ex: 01/2024"
              required
              pattern="\d{2}/\d{4}"
              title="Formato MM/AAAA"
              className="w-full px-3 py-2 rounded-md border bg-background text-sm focus:outline-none focus:ring-2 focus:ring-ring"
            />
          </div>

          {/* 2FA opcional */}
          <div className="space-y-1">
            <button
              type="button"
              onClick={() => setMostrarMfa(v => !v)}
              className="text-xs text-primary hover:underline"
            >
              {mostrarMfa ? '− Ocultar' : '+ Informar código 2FA'} (gov.br)
            </button>
            {mostrarMfa && (
              <input
                value={codigoMfa}
                onChange={e => setCodigoMfa(e.target.value)}
                placeholder="Código 2FA do gov.br (6 dígitos)"
                maxLength={8}
                className="w-full px-3 py-2 rounded-md border bg-background text-sm focus:outline-none focus:ring-2 focus:ring-ring"
              />
            )}
          </div>

          {erro && <p className="text-sm text-destructive">{erro}</p>}

          <button
            type="submit"
            disabled={enviando}
            className="w-full py-2 rounded-md bg-primary text-primary-foreground text-sm font-medium hover:opacity-90 disabled:opacity-50"
          >
            {enviando ? 'Iniciando...' : 'Emitir DARF'}
          </button>
        </form>
      )}

      {/* Acompanhamento da tarefa */}
      {tarefa && (
        <div className="rounded-lg border bg-card p-6 space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium">Tarefa #{tarefa.id}</p>
              <p className="text-xs text-muted-foreground">
                {tarefa.parametros?.competencia as string} — {
                  empresas.find(e => e.id === tarefa.empresa_id)?.razao_social ?? `Empresa ${tarefa.empresa_id}`
                }
              </p>
            </div>
            <StatusBadge status={tarefa.status as StatusTarefa} />
          </div>

          {/* Progresso */}
          {(tarefa.status === 'PENDENTE' || tarefa.status === 'EM_EXECUCAO') && (
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <span className="animate-spin">⟳</span>
              <span>
                {tarefa.status === 'PENDENTE' ? 'Aguardando execução...' : 'Acessando e-CAC / DCTFWeb...'}
              </span>
            </div>
          )}

          {/* Resultado do DARF */}
          {tarefa.status === 'CONCLUIDA' && resultado && (
            <DarfCard resultado={resultado} />
          )}

          {/* Erro */}
          {tarefa.status === 'ERRO' && (
            <div className="rounded-md bg-destructive/10 border border-destructive/20 p-3">
              <p className="text-sm font-medium text-destructive">Falha na execução</p>
              <p className="text-xs text-muted-foreground mt-1">
                Verifique os logs da tarefa em Histórico → #{tarefa.id}.
              </p>
            </div>
          )}

          {(tarefa.status === 'CONCLUIDA' || tarefa.status === 'ERRO') && (
            <button
              onClick={handleNovaConsulta}
              className="text-sm text-primary hover:underline"
            >
              ← Nova consulta
            </button>
          )}
        </div>
      )}
    </div>
  )
}

function DarfCard({ resultado }: { resultado: DarfResultado }) {
  const fmt = (v: number | undefined) =>
    v != null ? v.toLocaleString('pt-BR', { minimumFractionDigits: 2 }) : '—'

  return (
    <div className="space-y-4">
      {/* Cabeçalho */}
      <div className="rounded-md bg-green-50 border border-green-200 p-3">
        <p className="text-sm font-semibold text-green-800">DARF emitido com sucesso</p>
        <p className="text-xs text-green-600">
          Competência {resultado.competencia} · Receita {resultado.codigo_receita || '2484'}
        </p>
      </div>

      {/* Valores */}
      <div className="grid grid-cols-2 gap-3">
        <Detalhe label="Valor Principal" valor={`R$ ${fmt(resultado.valor_principal)}`} />
        <Detalhe label="Multa" valor={`R$ ${fmt(resultado.valor_multa)}`} />
        <Detalhe label="Juros" valor={`R$ ${fmt(resultado.valor_juros)}`} />
        <Detalhe
          label="Total a Pagar"
          valor={`R$ ${fmt(resultado.valor_total)}`}
          destaque
        />
      </div>

      {/* Vencimento e identificação */}
      <div className="grid grid-cols-2 gap-3">
        <Detalhe label="Vencimento" valor={resultado.data_vencimento || '—'} />
        <Detalhe label="Nosso Número" valor={resultado.nosso_numero || '—'} />
      </div>

      {/* Código de barras */}
      {resultado.codigo_barras && (
        <div className="space-y-1">
          <p className="text-xs font-medium text-muted-foreground uppercase tracking-wide">Linha Digitável</p>
          <div className="rounded-md bg-muted p-2 flex items-center justify-between gap-2">
            <code className="text-xs break-all">{resultado.codigo_barras}</code>
            <button
              onClick={() => navigator.clipboard.writeText(resultado.codigo_barras)}
              className="text-xs text-primary hover:underline whitespace-nowrap"
              title="Copiar"
            >
              Copiar
            </button>
          </div>
        </div>
      )}
    </div>
  )
}

function Detalhe({ label, valor, destaque = false }: { label: string; valor: string; destaque?: boolean }) {
  return (
    <div className={`rounded-md border p-2 space-y-0.5 ${destaque ? 'border-primary/30 bg-primary/5' : ''}`}>
      <p className="text-[10px] text-muted-foreground uppercase tracking-wide">{label}</p>
      <p className={`text-sm font-semibold ${destaque ? 'text-primary' : ''}`}>{valor}</p>
    </div>
  )
}
