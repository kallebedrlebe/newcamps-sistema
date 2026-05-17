import { cn } from '@/lib/utils'
import type { StatusTarefa } from '@/types/tarefa'

const styles: Record<StatusTarefa, string> = {
  PENDENTE: 'bg-yellow-100 text-yellow-800',
  EM_EXECUCAO: 'bg-blue-100 text-blue-800',
  CONCLUIDA: 'bg-green-100 text-green-800',
  ERRO: 'bg-red-100 text-red-800',
}

const labels: Record<StatusTarefa, string> = {
  PENDENTE: 'Pendente',
  EM_EXECUCAO: 'Em execução',
  CONCLUIDA: 'Concluída',
  ERRO: 'Erro',
}

export default function StatusBadge({ status }: { status: StatusTarefa }) {
  return (
    <span className={cn('inline-flex items-center px-2 py-0.5 rounded text-xs font-medium', styles[status])}>
      {labels[status]}
    </span>
  )
}
