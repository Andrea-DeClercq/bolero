<script setup>
import { ref, defineEmits, defineProps, watch, inject, onMounted } from "vue";

const $api = inject("$api");

const emits = defineEmits(["update:selectedAuthors"]);
const props = defineProps({
  selectedAuthors: {
    type: Array,
    default: () => [],
  },
});

// Champs de recherche
const searchNom = ref("");
const searchPrenom = ref("");
const searchIdRef = ref("");

// Liste des auteurs et sélection
const authors = ref([]);
const selectedAuthors = ref([...props.selectedAuthors]);
const currentPage = ref(1);
const limit = ref(20);
const totalItems = ref(0);

const searchAuthors = async (page = 1) => {
  currentPage.value = page;
  try {
    const params = {
      page: currentPage.value,
      limit: limit.value,
    };
    if (searchNom.value) params.nom = searchNom.value;
    if (searchPrenom.value) params.prenom = searchPrenom.value;
    if (searchIdRef.value) params.id_ref = searchIdRef.value;

    const response = await $api.auteur.getAuteurs(params);
    if (response.status === 200) {
      authors.value = response.data.auteurs;
      totalItems.value = response.data.total || 0;
    }
  } catch (error) {
    console.error("Erreur lors de la recherche d'auteurs :", error);
  }
};

const toggleAuthorSelection = (author) => {
  const index = selectedAuthors.value.findIndex((a) => a.id === author.id);
  if (index === -1) {
    selectedAuthors.value.push(author);
  } else {
    selectedAuthors.value.splice(index, 1);
  }
  emits("update:selectedAuthors", selectedAuthors.value);
};

const isSelected = (author) => selectedAuthors.value.some((a) => a.id === author.id);

onMounted(() => {
  searchAuthors();
});
</script>

<template lang="pug">
  div
    form(@submit.prevent="searchAuthors(1)").pb-3
      .row.mb-2
        .col
          label.form-label Nom :
          input.form-control(type="text" v-model="searchNom" placeholder="Rechercher par nom")
        .col
          label.form-label Prénom :
          input.form-control(type="text" v-model="searchPrenom" placeholder="Rechercher par prénom")
        .col
          label.form-label ID Référence :
          input.form-control(type="text" v-model="searchIdRef" placeholder="Rechercher par ID")
        .col-auto.d-flex.align-items-end
          button.btn.btn-primary(type="submit") Rechercher

    .author-list-modal(v-if="authors.length > 0")
      ul.list-group
        li.list-group-item(
          v-for="author in authors"
          :key="author.id"
          :class="{ 'active': isSelected(author) }"
          @click="toggleAuthorSelection(author)"
          role="button"
        )
          span(v-if="author.id_ref") {{ author.nom }} {{ author.prenom }} (IDREF : {{author.id_ref}})
          span(v-else) {{ author.nom }} {{ author.prenom }}
          font-awesome-icon.ms-2(
            v-if="isSelected(author)"
            icon="check-circle"
            class="text-secondary"
          )

      div.d-flex.justify-content-center.mt-3
        pagination(
          :options="{ hideCount: true }"
          v-model="currentPage"
          :records="totalItems"
          :per-page="limit"
          @paginate="searchAuthors"
        )

    p.text-muted(v-else) Aucun auteur trouvé.
</template>

<style scoped>
.author-list-modal {
  max-height: 300px;
  overflow-y: auto;
  padding: 0.5rem;
}

.list-group-item.active {
  background-color: #436666 !important;
  color: white;
  font-weight: bold;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>