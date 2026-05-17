import { useNavigate } from 'react-router-dom'
import { useEmpresas } from '@/hooks/useEmpresa'
import DataTable from '@/components/shared/DataTable'
import type { Empresa } from '@/types/empresa'

export default function EmpresasPage() {
  const { data: empresas = [], isLoading } = useEmpresas()
  const navigate = useNavigate()

  const columns = [
    { header: 'Razão Social', accessor: 'razao_social' as keyof Empresa },
    { header: 'CNPJ', accessor: (e: Empresa) => e.cnpj.replace(/(\d{2})(\d{3})(\d{3})(\d{4})(\d{2})/, '$1.$2.$3/$4-$5') },
    { header: 'Status', accessor: (e: Empresa) => e.ativa ? 'Ativa' : 'Inativa' },
    {
      header: '',
      accessor: (e: Empresa) => (
        <button
          onClick={() => navigate(`/empresas/${e.id}`)}
          className="text-primary text-xs hover:underline"
        >
          Editar
        </button>
      ),
    },
  ]

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-semibold">Empresas</h1>
        <button
          onClick={() => navigate('/empresas/nova')}
          className="px-3 py-1.5 bg-primary text-primary-foreground text-sm rounded-md hover:opacity-90"
        >
          Nova Empresa
        </button>
      </div>
      {isLoading ? (
        <p className="text-sm text-muted-foreground">Carregando...</p>
      ) : (
        <DataTable columns={columns} data={empresas} keyField="id" />
      )}
    </div>
  )
}
