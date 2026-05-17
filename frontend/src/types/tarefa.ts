export type TipoTarefa =
  | 'ECAC_DARF'
  | 'ECAC_DEBITOS'
  | 'ECAC_PARCELAMENTO'
  | 'FGTS_SALDO'
  | 'FGTS_EXTRATO'
  | 'TRON_PROCESSAMENTO'
  | 'TRON_RELATORIO'

export type StatusTarefa = 'PENDENTE' | 'EM_EXECUCAO' | 'CONCLUIDA' | 'ERRO'

export interface Tarefa {
  id: number
  empresa_id: number
  tipo: TipoTarefa
  status: StatusTarefa
  parametros: Record<string, unknown> | null
  resultado: Record<string, unknown> | null
  criado_em: string
  atualizado_em: string
}

export interface LogExecucao {
  id: number
  tarefa_id: number
  nivel: 'INFO' | 'WARN' | 'ERROR'
  mensagem: string
  ts: string
}
