import { apiClient } from "./api-client"
import type {
  RegisterRequest,
  RegisterResponse,
  LoginRequest,
  LoginResponse,
  ActivateRequest,
  ResendActivationRequest,
  ForgotPasswordRequest,
  ResetPasswordRequest,
  RefreshTokenResponse,
  User,
} from "@/types/auth"

export async function register(
  data: RegisterRequest
): Promise<RegisterResponse> {
  const response = await apiClient.post<RegisterResponse>("/auth/users/", data)
  return response.data
}

export async function login(data: LoginRequest): Promise<LoginResponse> {
  const response = await apiClient.post<LoginResponse>(
    "/auth/jwt/create/",
    data
  )
  return response.data
}

export async function refreshToken(): Promise<RefreshTokenResponse> {
  const response = await apiClient.post<RefreshTokenResponse>(
    "/auth/jwt/refresh/",
    {}
  )
  return response.data
}

export async function activate(data: ActivateRequest): Promise<void> {
  await apiClient.post("/auth/users/activation/", data)
}

export async function resendActivation(
  data: ResendActivationRequest
): Promise<void> {
  await apiClient.post("/auth/users/resend_activation/", data)
}

export async function forgotPassword(
  data: ForgotPasswordRequest
): Promise<void> {
  await apiClient.post("/auth/users/reset_password/", data)
}

export async function resetPassword(data: ResetPasswordRequest): Promise<void> {
  await apiClient.post("/auth/users/reset_password_confirm/", data)
}

export async function getMe(): Promise<User> {
  const response = await apiClient.get<User>("/auth/users/me/")
  return response.data
}

export async function logout(): Promise<void> {
  await apiClient.post("/auth/logout/")
}
