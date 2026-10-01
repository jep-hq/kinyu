// frontend/composables/useFetchAPI.ts
import type { UseFetchOptions } from 'nuxt/app'
import { defu } from 'defu'

export const useFetchAPI = <T>(url: string, options: UseFetchOptions<T> = {}) => {
  const config = useRuntimeConfig()

  const defaults: UseFetchOptions<T> = {
    baseURL: config.public.apiBase || 'http://localhost:8000/api/v1',
    // key: url, // auto-generated

    // Pass cookies along (for HttpOnly JWT)
    credentials: 'include',

    onRequest({ request, options }) {
        // Add Authorization header from Zitadel Auth
        const { user } = useZitadelAuth()
        if (user.value?.access_token) {
          options.headers = options.headers || {}
          // @ts-ignore
          options.headers.Authorization = `Bearer ${user.value.access_token}`
        }
    },

    onResponse({ request, response, options }) {
      // Handle global success
    },

    async onResponseError({ request, response, options }) {
      if (response.status === 401) {
        // Handle unauthorized (e.g. redirect to login or try refresh)
        // const auth = useAuthStore()
        // await auth.refresh()
        // Or if handling simple cookie session:
        // navigateTo('/login')
      }
    }
  }

  // Deep merge options
  const params = defu(options, defaults)

  return useFetch(url, params)
}
