export interface User {
  id: number
  nome: string
  email: string
  is_admin: boolean
  criado_em: string
}

export interface UserCreate {
  nome: string
  email: string
  senha: string
  is_admin?: boolean
}
