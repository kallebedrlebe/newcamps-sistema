import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import api from '@/lib/api'
import type { Tarefa, LogExecucao, TipoTarefa } from '@/types/tarefa'

export function useTarefas(empresaId?: number, status?: string) {
  return useQuery<Tarefa[]>({
    queryKey: ['tarefas', empresaId, status],
    queryFn: async () => {
      const params: Record<string, unknown> = {}
      if (empresaId) params.empresa_id = empresaId
      if (status) params.status = status
      const { data } = await api.get('/tarefas', { params })
      return data
    },
  })
}

export function useTarefa(id: number) {
  return useQuery<Tarefa>({
    queryKey: ['tarefas', id],
    queryFn: () => api.get(`/tarefas/${id}`).then(r => r.data),
    enabled: !!id,
    refetchInterval: (query) => {
      const data = query.state.data as Tarefa | undefined
      return data?.status === 'PENDENTE' || data?.status === 'EM_EXECUCAO' ? 3000 : false
    },
  })
}

export function useTarefaLogs(tarefaId: number) {
  return useQuery<LogExecucao[]>({
    queryKey: ['tarefas', tarefaId, 'logs'],
    queryFn: () => api.get(`/tarefas/${tarefaId}/logs`).then(r => r.data),
    enabled: !!tarefaId,
  })
}

export function useDisparaTarefa(endpoint: string) {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (params: Record<string, unknown>) =>
      api.post(endpoint, null, { params }).then(r => r.data as Tarefa),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['tarefas'] }),
  })
}
