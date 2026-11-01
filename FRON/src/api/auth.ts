import { api } from './client'
import type { LoginRequest, SignupRequest, Token, User, UserUpdate } from './types'

export const authApi = {
  signup: (data: SignupRequest) =>
    api.post<User>('/api/auth/signup', data).then((r) => r.data),

  login: (data: LoginRequest) =>
    api.post<Token>('/api/auth/login', data).then((r) => r.data),

  logout: () =>
    api.post('/api/auth/logout').then((r) => r.data),

  getMe: () =>
    api.get<User>('/api/users/me').then((r) => r.data),

  updateMe: (data: UserUpdate) =>
    api.patch<User>('/api/users/me', data).then((r) => r.data),
}
