import { useState, FormEvent } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { useEmpresa, useCreateEmpresa, useUpdateEmpresa } from '@/hooks/useEmpresa'

export default function EmpresaFormPage() {
  const { id } = useParams()
  const isEdit = !!id && id !== 'nova'
  const navigate = useNavigate()

  const { data: empresa } = useEmpresa(isEdit ? Number(id) : 0)
  const createMutation = useCreateEmpresa()
  const updateMutation = useUpdateEmpresa(Number(id))

  const [razaoSocial, setRazaoSocial] = useState(empresa?.razao_social ?? '')
  const [cnpj, setCnpj] = useState(empresa?.cnpj ?? '')

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    if (isEdit) {
      await updateMutation.mutateAsync({ razao_social: razaoSocial })
    } else {
      await createMutation.mutateAsync({ razao_social: razaoSocial, cnpj })
    }
    navigate('/empresas')
  }

  return (
    <div className="max-w-md space-y-4">
      <h1 className="text-xl font-semibold">{isEdit ? 'Editar Empresa' : 'Nova Empresa'}</h1>
      <form onSubmit={handleSubmit} className="space-y-4 rounded-lg border p-6 bg-card">
        <div className="space-y-1">
          <label className="text-sm font-medium">Razão Social</label>
          <input
            value={razaoSocial}
            onChange={e => setRazaoSocial(e.target.value)}
            required
            className="w-full px-3 py-2 rounded-md border bg-background text-sm focus:outline-none focus:ring-2 focus:ring-ring"
          />
        </div>
        {!isEdit && (
          <div className="space-y-1">
            <label className="text-sm font-medium">CNPJ (somente números)</label>
            <input
              value={cnpj}
              onChange={e => setCnpj(e.target.value.replace(/\D/g, ''))}
              maxLength={14}
              required
              placeholder="00000000000000"
              className="w-full px-3 py-2 rounded-md border bg-background text-sm focus:outline-none focus:ring-2 focus:ring-ring"
            />
          </div>
        )}
        <button
          type="submit"
          className="w-full py-2 rounded-md bg-primary text-primary-foreground text-sm font-medium hover:opacity-90"
        >
          {isEdit ? 'Salvar' : 'Cadastrar'}
        </button>
      </form>
    </div>
  )
}
