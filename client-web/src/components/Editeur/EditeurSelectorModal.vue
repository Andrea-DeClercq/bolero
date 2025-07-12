<script setup>
import { ref, watch, inject, defineProps, defineEmits } from 'vue';

const props = defineProps({
  selectedEditeur: Object,
});
const emits = defineEmits(['update:selectedEditeur', 'close']);

const $api = inject('$api');
const authStore = inject('authStore');
const { handleError } = inject('errorHandler');

const search = ref('');
const editeurs = ref([]);
const currentPage = ref(1);
const limit = 50;
const total = ref(0);
const totalPages = ref(0);
const loading = ref(false);

const nouveauNom = ref('');

const createEditeur = async () => {
  const nom = nouveauNom.value.trim();
  if (!nom) return;
  try {
    const response = await $api.editeur.postEditeur(authStore.getToken(), { nom: nom});
    if (response.status === 200 || response.status === 201) {
      emits('update:selectedEditeur', {
        id: response.data.id,
        nom: response.data.nom
      });
      nouveauNom.value = '';
      emits('close');
    }
  } catch (err) {
    handleError(err, "Erreur lors de la création de l'éditeur");
  }
};

const fetchEditeurs = async () => {
  loading.value = true;
  try {
    const response = await $api.editeur.getEditeurs({
      nom: search.value || undefined,
      page: currentPage.value,
      limit: limit,
    });
    editeurs.value = response.data.editeurs;
    total.value = response.data.total;
    totalPages.value = response.data.pages;
  } catch (err) {
    handleError(err, "Erreur lors du chargement des éditeurs");
  } finally {
    loading.value = false;
  }
};

watch(search, () => {
  currentPage.value = 1;
});

watch([search, currentPage], fetchEditeurs, { immediate: true });

const selectEditeur = (editeur) => {
  emits('update:selectedEditeur', editeur);
  emits('close');
};

const closeModal = () => {
  emits('close');
};
</script>

<template lang="pug">
.modal-backdrop(@click.self="closeModal")
  .modal-content(@click.stop)
    .modal-header.d-flex.justify-content-between.pb-4
      h5.modal-title Sélectionner un éditeur
      button.btn-close(@click="closeModal")

    .modal-body
      input.form-control.mb-3(
        v-model="search",
        placeholder="Rechercher un éditeur"
      )

      div(v-if="loading") Chargement...
      ul.list-group(v-else)
        li.list-group-item.list-group-item-action(
          v-for="editeur in editeurs",
          :key="editeur.id",
          @click="selectEditeur(editeur)"
        ) {{ editeur.nom }}
      hr
      .mt-4
        label.form-label.mb-1 Ajouter un nouvel éditeur :
        .input-group
          input.form-control(
            v-model="nouveauNom",
            placeholder="Nom de l'éditeur"
          )
          button.btn.btn-success(@click="createEditeur") Ajouter

      .d-flex.justify-content-center.mt-3(v-if="total > limit")
        pagination(
          :options="{ hideCount: true }"
          v-model="currentPage"
          :records="total"
          :per-page="limit"
        )
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
</style>