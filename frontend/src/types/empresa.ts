export interface Empresa {
  id: number
  razao_social: string
  cnpj: string
  ativa: boolean
  criado_em: string
}

export interface EmpresaCreate {
  razao_social: string
  cnpj: string
  credenciais?: Record<string, string>
}

export interface EmpresaUpdate {
  razao_social?: string
  credenciais?: Record<string, string>
  ativa?: boolean
}
