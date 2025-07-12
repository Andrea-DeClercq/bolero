<script setup>
import { inject, ref, computed, onMounted } from "vue";
import { useSearchFields } from "@/composables/useSearchFields";
import { useSearchParams } from "@/composables/useSearchParams";
import { ouvrageSearchConfig } from "@/composables/searchFieldsConfig";

// Dépendances
const $api = inject('$api');
const navigation = inject('navigation');
const authStore = inject('authStore');
const { handleError, resetError } = inject('errorHandler');
const { buildParams, buildExportParams } = useSearchParams();

// Variables
const { searchFields, fixedValues, addField, removeField, removeAllFields, filteredAvailableFields, updateAvailableFields } = 
    useSearchFields(ouvrageSearchConfig.availableFields, ouvrageSearchConfig.fixedFields);

const filteredOuvrages = ref([]);
const currentPage = ref(1);
const limit = ref(100);
const totalItems = ref(0);
const sortField = ref("id");
const sortOrder = ref("asc");
const isExporting = ref(false);

const totalPages = computed(() => Math.ceil(totalItems.value / limit.value));

const searchOuvrages = async (page) => {
  resetError();
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
    const response = await $api.ouvrage.getOuvrages(params);
    filteredOuvrages.value = response.data.ouvrages || [];
    totalItems.value = response.data.total || 0;
  } catch (error) {
    handleError(error, "Erreur lors du chargement des ouvrages");
  }
};

const setSort = (field) => {
  if (sortField.value === field) {
    sortOrder.value = sortOrder.value === 'asc' ? 'desc' : 'asc';
  } else {
    sortField.value = field;
    sortOrder.value = 'asc';
  }
  searchOuvrages(1);
};

async function exportCsv() {
  isExporting.value = true;
  try {
    const params = buildExportParams({
      fixedValues,
      searchFields: searchFields.value,
    });
    const blob = await $api.ouvrage.exportOuvrages(params);
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.setAttribute("download", "ouvrages.csv");
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
  searchOuvrages(1);
});
</script>


<template lang="pug">
  form(@submit.prevent="searchOuvrages(1)").pb-4
    h2.text-center.py-2 Rechercher dans les ouvrages

    //- Champs fixes (responsive)
    .row.mb-3
      .col-12.col-md-4.d-flex.align-items-end.mb-2
        input.form-control(type="text" placeholder="Titre" v-model="fixedValues.titre")
      .col-12.col-md-4.d-flex.align-items-end.mb-2
        input.form-control(type="text" placeholder="Éditeur" v-model="fixedValues.editeur")
      .col-12.col-md-4.d-flex.align-items-end.mb-2
        input.form-control(type="text" placeholder="Année de parution" v-model="fixedValues.anneeParution")

    //- Champs dynamiques
    .row.mb-3(v-for="(field, index) in searchFields" :key="index")
      .col-12.col-md-5.d-flex.align-items-end.mb-2
        select.form-select(v-model="field.key" @change="updateAvailableFields")
          option(value="" disabled) -- Choisir un champ --
          option(
            v-for="option in filteredAvailableFields(index)" 
            :value="option.key" 
            :key="option.key"
          ) {{ option.label }}
      .col-12.col-md-5.d-flex.align-items-end.mb-2
        input.form-control(
          type="text"
          :placeholder="field.key ? `Recherche ${field.key}` : 'Sélectionner un champ'"
          v-model="field.value"
          @keydown.enter.prevent="searchOuvrages(1)"
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
        button.btn.btn-success(
          v-if="authStore.isAuthenticated"
          type="button"
          @click="navigation.goToAddOuvrage()")
          font-awesome-icon(icon="plus-circle" class="me-2")
          | Ajouter un ouvrage

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

  //- TABLE DESKTOP
  div.d-none.d-md-block
    div.table-responsive
      table.table.table-bordered.table-hover
        thead
          tr.text-center
            th(style="width: 5%" role="button" @click="setSort('id')") ID
              font-awesome-icon.mx-2(:icon="sortField === 'id' ? (sortOrder === 'asc' ? 'sort-up' : 'sort-down') : 'sort'")
            th(style="width: 30%" role="button" @click="setSort('titre')") Titre - Sous-titre
              font-awesome-icon.mx-2(:icon="sortField === 'titre' ? (sortOrder === 'asc' ? 'sort-up' : 'sort-down') : 'sort'")
            th(style="width: 10%") Auteur(s)
            th(style="width: 10%" role="button" @click="setSort('ean')") EAN
              font-awesome-icon.mx-2(:icon="sortField === 'ean' ? (sortOrder === 'asc' ? 'sort-up' : 'sort-down') : 'sort'")
            th(style="width: 10%" role="button" @click="setSort('doi')") DOI
              font-awesome-icon.mx-2(:icon="sortField === 'doi' ? (sortOrder === 'asc' ? 'sort-up' : 'sort-down') : 'sort'")
            th(style="width: 10%" role="button" @click="setSort('editeur')") Éditeur
              font-awesome-icon.mx-2(:icon="sortField === 'editeur' ? (sortOrder === 'asc' ? 'sort-up' : 'sort-down') : 'sort'")
            th(style="width: 15%" role="button" @click="setSort('annee_parution')") Année de parution
              font-awesome-icon.mx-2(:icon="sortField === 'annee_parution' ? (sortOrder === 'asc' ? 'sort-up' : 'sort-down') : 'sort'")
            th(style="width: 5%") Recensions

        tbody
          tr(v-if="filteredOuvrages.length === 0")
            td.text-center(colspan=8) Aucun ouvrage trouvé
          tr.text-center(v-for="ouvrage in filteredOuvrages" :key="ouvrage.id" @click="navigation.goToOuvrage(ouvrage.id)" role="button")
            td {{ ouvrage.id }}
            td
              span(v-html="ouvrage.titre")
              p(v-if="ouvrage['sous_titre']") —
                span.px-1(v-html="ouvrage['sous_titre']")
            td
              ul.list-unstyled.mb-0
                li(v-for="auteur in ouvrage['ouvrage_auteurs']" :key="auteur.auteur.id")
                  span {{ auteur.auteur.prenom }} {{ auteur.auteur.nom }}
            td {{ ouvrage.ean }}
            td {{ ouvrage.doi || 'N/A' }}
            td {{ ouvrage.editeur }}
            td {{ ouvrage['annee_parution'] }}
            td {{ ouvrage.ouvrage_recensions.length }}

  //- CARTES MOBILE
  div.d-md-none
    div(v-if="filteredOuvrages.length === 0").text-center.mt-3 Aucun ouvrage trouvé
    div(v-else v-for="ouvrage in filteredOuvrages" :key="ouvrage.id" class="card mb-2" @click="navigation.goToOuvrage(ouvrage.id)" role="button")
      div.card-body
        h5.card-title.mb-1 {{ ouvrage.titre }}
        p.mb-1(v-if="ouvrage['sous_titre']") Sous-titre : {{ ouvrage.sous_titre }}
        p.mb-1 Année : {{ ouvrage.annee_parution }}
        p.mb-1 Éditeur : {{ ouvrage.editeur }}
        p.mb-1 DOI : {{ ouvrage.doi || 'N/A' }}
        p.mb-1 EAN : {{ ouvrage.ean }}
        p.mb-1 Recensions : {{ ouvrage.ouvrage_recensions.length }}
        p.mb-0 Auteur(s) :
        ul
          li(v-for="auteur in ouvrage.ouvrage_auteurs" :key="auteur.auteur.id")
            | {{ auteur.auteur.prenom }} {{ auteur.auteur.nom }}

  //- PAGINATION
  div.d-flex.justify-content-center.mt-3(v-if="totalItems > 0")
    pagination(
      :options="{ hideCount: true }"
      v-model="currentPage"
      :records="totalItems"
      :per-page="limit"
      @paginate="searchOuvrages"
    )
</template>