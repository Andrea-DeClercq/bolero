<script setup>
import { ref, watch, defineEmits, defineProps } from "vue";
import AuteurListModal from "@/components/Auteur/AuteurListModal.vue";
import AuteurForm from "@/views/Auteurs/AuteurForm.vue";

const emits = defineEmits(["update:selectedAuthors", "close"]);
const props = defineProps({
  selectedAuthors: {
    type: Array,
    default: () => []
  }
});

const selectedAuthors = ref([...props.selectedAuthors]);
const mode = ref("select");

watch(
  () => props.selectedAuthors,
  (newVal) => {
    selectedAuthors.value = [...newVal];
  }
);

const handleAuthorCreated = (author) => {
  selectedAuthors.value.push(author);
  emits("update:selectedAuthors", [...selectedAuthors.value]);
  emits("close");
};

const confirmSelection = () => {
  emits("update:selectedAuthors", [...selectedAuthors.value]);
  emits("close");
};

const closeModal = () => {
  emits("close");
};
</script>

<template lang="pug">
div.modal-backdrop(@click.self="closeModal")
  div.modal-content(@click.stop)
    div.modal-header.d-flex.justify-content-between
      h5.modal-title Sélectionner ou créer un auteur
      button.btn-close(@click="closeModal")

    div.modal-body
      .btn-group.mb-3
        button.btn.btn-outline-primary(:class="{ active: mode === 'select' }", @click="mode = 'select'")
          font-awesome-icon(icon="search")
          |  Rechercher
        button.btn.btn-outline-success(:class="{ active: mode === 'create' }", @click="mode = 'create'")
          font-awesome-icon(icon="plus")
          |  Créer un auteur

      AuteurListModal(
        v-if="mode === 'select'"
        :selectedAuthors="selectedAuthors"
        @update:selectedAuthors="selectedAuthors = $event"
      )

      AuteurForm(
        v-if="mode === 'create'"
        @auteurCreated="handleAuthorCreated"
      )

    div.modal-footer.d-flex(v-if="mode === 'select'")
      button.btn.btn-secondary(@click="closeModal") Annuler
      button.btn.btn-primary.m-2(
        @click="confirmSelection"
        :disabled="selectedAuthors.length === 0"
      ) Valider
</template>

<style scoped>
.modal-backdrop {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
}
.modal-content {
  background: white;
  padding: 1rem;
  width: 80%;
  border-radius: 5px;
  max-height: 90vh;
  overflow-y: auto;
}
.btn-group .btn.active {
  background-color: #436666;
  color: white;
}
</style>