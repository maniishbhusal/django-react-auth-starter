import { useMutation } from "@tanstack/react-query"
import { AxiosError } from "axios"
import {
  register,
  login as loginApi,
  activate,
  resendActivation,
  forgotPassword,
  resetPassword,
} from "@/lib/auth-api"
import { useAuth } from "@/hooks/use-auth"
import type {
  RegisterRequest,
  RegisterResponse,
  LoginRequest,
  LoginResponse,
  ActivateRequest,
  ResendActivationRequest,
  ForgotPasswordRequest,
  ResetPasswordRequest,
  ApiError,
} from "@/types/auth"

export function useRegister() {
  return useMutation<RegisterResponse, AxiosError<ApiError>, RegisterRequest>({
    mutationFn: register,
  })
}

export function useLogin() {
  const { login } = useAuth()

  return useMutation<LoginResponse, AxiosError<ApiError>, LoginRequest>({
    mutationFn: loginApi,
    onSuccess: async (data) => {
      await login({
        access: data.access,
        refresh: data.refresh,
      })
    },
  })
}

export function useActivate() {
  return useMutation<void, AxiosError<ApiError>, ActivateRequest>({
    mutationFn: activate,
  })
}

export function useResendActivation() {
  return useMutation<void, AxiosError<ApiError>, ResendActivationRequest>({
    mutationFn: resendActivation,
  })
}

export function useForgotPassword() {
  return useMutation<void, AxiosError<ApiError>, ForgotPasswordRequest>({
    mutationFn: forgotPassword,
  })
}

export function useResetPassword() {
  return useMutation<void, AxiosError<ApiError>, ResetPasswordRequest>({
    mutationFn: resetPassword,
  })
}
