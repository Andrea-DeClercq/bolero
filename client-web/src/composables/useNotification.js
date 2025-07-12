import { ref, computed, watch } from 'vue'

export function useNotification(errorHandler) {
  const message = ref(null)
  const type = ref(null)
  const visible = ref(false)

  function notify(msg, msgType = 'info') {
    message.value = msg
    type.value = msgType
    visible.value = true

    setTimeout(() => {
      clear();
    }, 3000);
  }

  function clear() {
    message.value = null
    type.value = null
    visible.value = false
    if (errorHandler) {
      errorHandler.resetError(); // on reset aussi l'erreur liée
    }
  }

  const error = computed(() => errorHandler.error.value)
  const hasError = computed(() => errorHandler.hasError.value)

  watch(hasError, (newVal) => {
    if (newVal) {
      message.value = error.value;
      type.value = 'danger';
      visible.value = true;

      setTimeout(() => {
        clear();
      }, 5000); // délai un peu plus long pour lire l'erreur
    }
  });

  return {
    message,
    type,
    visible,
    notify,
    clear,
    error,
    hasError,
  }
}