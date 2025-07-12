import { ref } from 'vue'
import axios from 'axios'

export function useErrorHandler() {
  const error = ref(null)
  const hasError = ref(false)

  function handleError(err, contextMessage = 'Une erreur est survenue') {
    console.error(`${contextMessage} :`, err)

    // Gère aussi bien une exception JS qu'une réponse API mal formatée
    // TODO: Gérer les messages d'erreurs lié au serveur. Dans error.py
    if (axios.isAxiosError(err)) {
      error.value = err.response?.data?.data?.description || err.response?.data?.message || err.message || 'Erreur API'
    } else if (typeof err === 'string') {
      error.value = err
    } else {
      error.value = 'Erreur inconnue'
    }

    hasError.value = true
  }

  function resetError() {
    hasError.value = false
    error.value = null
  }

  return {
    error,
    hasError,
    handleError,
    resetError
  }
}