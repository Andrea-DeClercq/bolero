<script setup>
import { inject, ref, computed, onMounted } from "vue";
import { useSearchFields } from "@/composables/useSearchFields";
import { useSearchParams } from "@/composables/useSearchParams";
import { recensionSearchConfig } from "@/composables/searchFieldsConfig";

// Dépendances
const $api = inject('$api');
const navigation = inject('navigation');
const authStore = inject('authStore');
const { handleError, resetError } = inject('errorHandler');
const { buildParams, buildExportParams } = useSearchParams();

// Variables
const { searchFields, fixedValues, addField, removeField, removeAllFields, filteredAvailableFields, updateAvailableFields } = 
    useSearchFields(recensionSearchConfig.availableFields, recensionSearchConfig.fixedFields);

const filteredRecensions = ref([]);
const currentPage = ref(1);
const limit = ref(100);
const totalItems = ref(0);
const sortField = ref("id");
const sortOrder = ref("asc");
const isExporting = ref(false);

const totalPages = computed(() => Math.ceil(totalItems.value / limit.value));

const searchRecensions = async (page) => {
  resetError()
  currentPage.value = page;
  const params = buildParams({
    page: currentPage.value,
    limit: limit.value,
    sort: sortField.value,
    order: sortOrder.value,
    fixedValues,
    searchFields: searchFields.value
  });
  try {
    const response = await $api.recension.getRecensions(params);
    filteredRecensions.value = response.data.recensions || [];
    totalItems.value = response.data.total || 0;
  } catch (error) {
    handleError(error, "Erreur lors du chargement des recensions");
  }
};

const setSort = (field) => {
  if (sortField.value === field) {
    sortOrder.value = sortOrder.value === 'asc' ? 'desc' : 'asc';
  } else {
    sortField.value = field;
    sortOrder.value = 'asc';
  }
  searchRecensions(1);
};

async function exportCsv() {
  isExporting.value = true;
  try {
    const params = buildExportParams({
      fixedValues,
      searchFields: searchFields.value
    });

    const blob = await $api.recension.exportRecensions(params);
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.setAttribute("download", "recensions.csv");
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  } catch (error) {
    handleError(error, "Erreur lors de l’export CSV");
  } finally {
    isExporting.value = false;
  }
}

onMounted(() => {
  searchRecensions(1);
});
</script>

<template lang="pug">
  form(@submit.prevent="searchRecensions(1)").pb-4
    h2.text-center.py-2 Rechercher dans les recensions

    //- Champs fixes
    .row.mb-3
      .col-12.col-md-4.d-flex.align-items-end.mb-2
        input.form-control(type="text" placeholder="Titre" v-model="fixedValues.titre")
      .col-12.col-md-4.d-flex.align-items-end.mb-2
        input.form-control(type="text" placeholder="Titre de la revue" v-model="fixedValues['titre_revue']")
      .col-12.col-md-4.d-flex.align-items-end.mb-2
        input.form-control(type="text" placeholder="Année" v-model="fixedValues.annee")

    //- Champs dynamiques
    .row.mb-3(v-for="(field, index) in searchFields" :key="index")
      .col-12.col-md-5.d-flex.align-items-end.mb-2
        select.form-select(v-model="field.key" @change="updateAvailableFields")
          option(value="" disabled) -- Choisir un champ --
          option(v-for="option in filteredAvailableFields(index)" :value="option.key" :key="option.key") {{ option.label }}
      .col-12.col-md-5.d-flex.align-items-end.mb-2
        input.form-control(
          type="text"
          :placeholder="field.key ? `Recherche ${field.key}` : 'Sélectionner un champ'"
          v-model="field.value"
          @keydown.enter.prevent="searchRecensions(1)"
          :disabled="!field.key"
        )
      .col-12.col-md-2.d-flex.align-items-center.mb-2
        font-awesome-icon.text-danger.cursor-pointer(
          v-if="searchFields.length > 0"
          icon="times-circle"
          type="button"
          size="lg"
          @click.prevent="removeField(index)"
        )

    .row.mb-3
      .col-12.col-md-6.d-flex.align-items-end.mb-2
        button.btn.btn-secondary(type="button" @click.prevent="addField") Ajouter un champ
        button.btn.btn-light.ms-2(type="button" @click.prevent="removeAllFields") Supprimer tous les champs

      .col-12.col-md-6.d-flex.align-items-end.justify-content-md-end.mb-2
        button.btn.btn-success(v-if="authStore.isAuthenticated" type="button" @click="navigation.goToAddRecension()")
          font-awesome-icon(icon="plus-circle" class="me-2")
          | Ajouter une recension
        button.btn.btn-outline-info.ms-2(
          type="button"
          :disabled="isExporting"
          @click="exportCsv")
          font-awesome-icon(
            :icon="isExporting ? 'spinner' : 'download'" 
            class="me-2"
            :class="{ 'fa-spin': isExporting }"
          )
          | {{ isExporting ? 'Export en cours...' : 'Export résultats CSV' }}

        button.btn.btn-primary.ms-2(type="submit") Rechercher

  // Version desktop
  div.d-none.d-md-block
    div.table-responsive
      table.table.table-bordered.table-hover
        thead
          tr.text-center
            th(style="width: 5%" role="button" @click="setSort('id')") ID
              font-awesome-icon.mx-2(:icon="sortField === 'id' ? (sortOrder === 'asc' ? 'sort-up' : 'sort-down') : 'sort'")
            th(style="width: 30%" role="button" @click="setSort('titre')") Titre - Sous-titre
              font-awesome-icon.mx-2(:icon="sortField === 'titre' ? (sortOrder === 'asc' ? 'sort-up' : 'sort-down') : 'sort'")
            th(style="width: 20%" role="button" @click="setSort('titre_revue')") Titre de la revue
              font-awesome-icon.mx-2(:icon="sortField === 'titre_revue' ? (sortOrder === 'asc' ? 'sort-up' : 'sort-down') : 'sort'")
            th(style="width: 20%") Auteur(s)
            th(style="width: 15%" role="button" @click="setSort('doi')") DOI
              font-awesome-icon.mx-2(:icon="sortField === 'doi' ? (sortOrder === 'asc' ? 'sort-up' : 'sort-down') : 'sort'")
            th(style="width: 10%" role="button" @click="setSort('annee')") Année
              font-awesome-icon.mx-2(:icon="sortField === 'annee' ? (sortOrder === 'asc' ? 'sort-up' : 'sort-down') : 'sort'")
        tbody
          tr(v-if="filteredRecensions.length === 0")
            td.text-center(colspan=6) Aucune recension trouvée
          tr.text-center(v-for="recension in filteredRecensions" :key="recension.id" @click="navigation.goToRecension(recension.id)" role="button")
            td {{ recension.id }}
            td
              span(v-html="recension.titre")
              span(v-if="recension['sous-titre']") —
                span.px-1(v-html="recension['sous-titre']")
            td {{ recension['titre_revue'] }}
            td
              ul.list-unstyled.mb-0
                li(v-for="auteur in recension['recension_auteurs']" :key="auteur.auteur.id")
                  | {{ auteur.auteur.prenom }} {{ auteur.auteur.nom }}
            td {{ recension.doi || 'N/A' }}
            td {{ recension.annee }}

  // Version mobile
  div.d-md-none
    div(v-if="filteredRecensions.length === 0").text-center.mt-3 Aucune recension trouvée
    div(v-else v-for="recension in filteredRecensions" :key="recension.id" class="card mb-2" @click="navigation.goToRecension(recension.id)" role="button")
      div.card-body
        h5.card-title.mb-1(v-html="recension.titre")
        p.mb-1(v-if="recension['sous-titre']") Sous-titre : 
          span(v-html="recension['sous-titre']")
        p.mb-1 Revue : {{ recension['titre_revue'] }}
        p.mb-1 Année : {{ recension.annee }}
        p.mb-1 DOI : {{ recension.doi || 'N/A' }}
        p.mb-0 Auteur(s) :
          ul.list-unstyled
            li(v-for="auteur in recension['recension_auteurs']" :key="auteur.auteur.id")
              | {{ auteur.auteur.prenom }} {{ auteur.auteur.nom }}

  div.d-flex.justify-content-center.mt-3
    pagination(
      :options="{ hideCount: true }"
      v-model="currentPage"
      :records="totalItems"
      :per-page="limit"
      @paginate="searchRecensions"
    )
</template>

<style scoped>
table {
  table-layout: fixed;
  width: 100%;
}

@media (max-width: 768px) {
  table {
    font-size: 0.85rem;
  }

  .card {
    cursor: pointer;
  }

  .card p {
    font-size: 0.9rem;
  }
}
</style>