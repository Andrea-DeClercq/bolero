<script setup>
import { ref, watch, inject, defineProps, defineEmits } from 'vue';

const props = defineProps({
  selectedRevue: Object,
});
const emits = defineEmits(['update:selectedRevue', 'close']);

const $api = inject('$api');
const authStore = inject('authStore');
const { handleError } = inject('errorHandler');

const search = ref('');
const revues = ref([]);
const currentPage = ref(1);
const limit = 50;
const total = ref(0);
const totalPages = ref(0);
const loading = ref(false);

const nouveauTitre = ref('');

const createRevue = async () => {
  const titre = nouveauTitre.value.trim();
  if (!titre) return;
  try {
    const response = await $api.revue.postRevue(authStore.getToken(), { titre: titre});
    if (response.status === 200 || response.status === 201) {
      emits('update:selectedRevue', {
        id: response.data.id,
        titre: response.data.titre
      });
      nouveauTitre.value = '';
      emits('close');
    }
  } catch (err) {
    handleError(err, "Erreur lors de la création de la revue");
  }
};

const fetchRevues = async () => {
  loading.value = true;
  try {
    const response = await $api.revue.getRevues({
      titre: search.value || undefined,
      page: currentPage.value,
      limit: limit,
    });
    revues.value = response.data.revues;
    total.value = response.data.total;
    totalPages.value = response.data.pages;
  } catch (err) {
    handleError(err, "Erreur lors du chargement des revues");
  } finally {
    loading.value = false;
  }
};

watch(search, () => {
  currentPage.value = 1;
});

watch([search, currentPage], fetchRevues, { immediate: true });

const selectRevue = (revue) => {
  emits('update:selectedRevue', revue);
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
      h5.modal-title Sélectionner une revue
      button.btn-close(@click="closeModal")

    .modal-body
      input.form-control.mb-3(
        v-model="search",
        placeholder="Rechercher une revue"
      )

      div(v-if="loading") Chargement...
      ul.list-group(v-else)
        li.list-group-item.list-group-item-action(
          v-for="revue in revues",
          :key="revue.id",
          @click="selectRevue(revue)"
        ) {{ revue.titre }}
      hr
      .mt-4
        label.form-label.mb-1 Ajouter une nouvelle revue :
        .input-group
          input.form-control(
            v-model="nouveauTitre",
            placeholder="Titre de la revue"
          )
          button.btn.btn-success(@click="createRevue") Ajouter

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