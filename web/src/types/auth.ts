export interface User {
  id: string
  email: string
  full_name: string
  agreed_to_terms: boolean
  agreed_at: string | null
  date_joined: string
}

export interface RegisterRequest {
  email: string
  username: string
  password: string
  re_password: string
  full_name: string
  agreed_to_terms: boolean
}

export interface RegisterResponse {
  id: string
  email: string
  full_name: string
}

export interface LoginRequest {
  email: string
  password: string
}

export interface LoginResponse {
  access: string
}

export interface ActivateRequest {
  uid: string
  token: string
}

export interface ResendActivationRequest {
  email: string
}

export interface ForgotPasswordRequest {
  email: string
}

export interface ResetPasswordRequest {
  uid: string
  token: string
  new_password: string
  re_new_password: string
}

export interface RefreshTokenResponse {
  access: string
}

export interface ApiError {
  [key: string]: string[] | string
}
