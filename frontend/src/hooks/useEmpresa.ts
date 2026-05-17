import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import api from '@/lib/api'
import type { Empresa, EmpresaCreate, EmpresaUpdate } from '@/types/empresa'

export function useEmpresas(ativa?: boolean) {
  return useQuery<Empresa[]>({
    queryKey: ['empresas', ativa],
    queryFn: async () => {
      const params = ativa !== undefined ? { ativa } : {}
      const { data } = await api.get('/empresas', { params })
      return data
    },
  })
}

export function useEmpresa(id: number) {
  return useQuery<Empresa>({
    queryKey: ['empresas', id],
    queryFn: async () => {
      const { data } = await api.get(`/empresas/${id}`)
      return data
    },
    enabled: !!id,
  })
}

export function useCreateEmpresa() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (body: EmpresaCreate) => api.post('/empresas', body).then(r => r.data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['empresas'] }),
  })
}

export function useUpdateEmpresa(id: number) {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (body: EmpresaUpdate) => api.put(`/empresas/${id}`, body).then(r => r.data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['empresas'] }),
  })
}
