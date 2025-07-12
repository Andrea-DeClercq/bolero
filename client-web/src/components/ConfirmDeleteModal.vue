<script setup>
import { defineProps, defineEmits } from "vue";

const props = defineProps({
  visible: Boolean,
  title: {
    type: String,
    default: "Supprimer l’élément"
  },
  message: {
    type: String,
    default: "Cette action supprimera également toutes les relations associées. Voulez-vous continuer ?"
  }
});

const emits = defineEmits(["confirm", "cancel"]);
</script>

<template lang="pug">
div.modal-backdrop(v-if="visible")
  div.modal-content(@click.stop)
    div.modal-header.d-flex.justify-content-between.align-items-start
      h5.modal-title {{ title }}
      button.btn-close(@click="emits('cancel')")

    div.modal-body
      p {{ message }}

    div.modal-footer.d-flex.justify-content-end
      button.btn.btn-secondary(@click="emits('cancel')") Annuler
      button.btn.btn-danger(@click="emits('confirm')") Supprimer
</template>

<style scoped>
.modal-backdrop {
  position: fixed;
  top: 0; left: 0;
  width: 100%; height: 100%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
}
.modal-content {
  background: white;
  padding: 1rem;
  width: 90%;
  max-width: 500px;
  border-radius: 5px;
}
.modal-header {
  border-bottom: 1px solid #ddd;
  margin-bottom: 1rem;
}
.modal-footer > * + * {
  margin-left: 0.5rem;
}
</style>