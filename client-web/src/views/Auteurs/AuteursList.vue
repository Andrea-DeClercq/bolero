<script setup>
import { inject, ref, reactive, computed, onMounted } from 'vue';
import { useSearchParams } from "@/composables/useSearchParams";

// Dépendances
const $api = inject('$api')
const navigation = inject('navigation');
const authStore = inject('authStore');
const { handleError, resetError } = inject('errorHandler');
const { buildParams, buildExportParams } = useSearchParams();

// Variables
const filteredAuteurs = ref([]);
const currentPage = ref(1);
const limit = 100;
const totalItems = ref(0);
const sortField = ref('id');
const sortOrder = ref('asc');
const filters = reactive({
});
const isExporting = ref(false);

const totalPages = computed(() => Math.ceil(totalItems.value / limit));

async function searchAuteurs(page = 1) {
  resetError()
  currentPage.value = page;

  const params = buildParams({
    page: currentPage.value,
    limit,
    sort: sortField.value,
    order: sortOrder.value,
    fixedValues: filters,
    searchFields: []
  });


  try {
    const response = await $api.auteur.getAuteurs(params);
    filteredAuteurs.value = response.data.auteurs || [];
    totalItems.value = response.data.total || 0;
  } catch (error) {
    handleError(error, "Erreur lors du chargement des auteurs")
  }
}

function setSort(field) {
  if (sortField.value === field) {
    sortOrder.value = sortOrder.value === 'asc' ? 'desc' : 'asc';
  } else {
    sortField.value = field;
    sortOrder.value = 'asc';
  }
  searchAuteurs(1);
}

function setFilter(key, value) {
  filters[key] = value
}

function onPageChange(page) {
  searchAuteurs(page)
}

function handleAuteurClick(id) {
  navigation.goToAuteur(id);
}

async function exportCsv() {
  isExporting.value = true;
  try {
    const params = buildExportParams({
      fixedValues: filters,
      searchFields: []
    });

    const blob = await $api.auteur.exportAuteurs(params);
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.setAttribute("download", "auteurs.csv");
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
  searchAuteurs(1)
})
</script>

<template lang="pug">
  form
    h2.text-center.py-2 Rechercher dans les auteurs
    .row.mb-3
      .col-12.col-md-4.d-flex.align-items-end.mb-2
        input.form-control(type="text" placeholder="ID Ref" @input="setFilter('id-ref', $event.target.value)")
  
      .col-12.col-md-4.d-flex.align-items-end.mb-2
        input.form-control(type="text" placeholder="Nom" @input="setFilter('nom', $event.target.value)")
  
      .col-12.col-md-4.d-flex.align-items-end.mb-2
        input.form-control(type="text" placeholder="Prénom" @input="setFilter('prenom', $event.target.value)")
  
    .row.mb-3
      .col-12.col-md-6.offset-md-6.d-flex.align-items-end.justify-content-md-end.mb-2
        button.btn.btn-success(v-if="authStore.isAuthenticated" type="button" @click="navigation.goToAddAuteur()")
          font-awesome-icon(icon="plus-circle" class="me-2")
          | Ajouter un auteur
        button.btn.btn-outline-info.ms-2(
          type="button"
          :disabled="isExporting"
          @click="exportCsv"
        )
          font-awesome-icon(
            :icon="isExporting ? 'spinner' : 'download'" 
            class="me-2"
            :class="{ 'fa-spin': isExporting }"
          )
          | {{ isExporting ? 'Export en cours...' : 'Export résultats CSV' }}
        button.btn.btn-primary.ms-2(@click.prevent="searchAuteurs(1)") Rechercher

  //- Table desktop
  div.d-none.d-md-block
    div.table-responsive
      table.table.table-bordered.table-hover
        thead
          tr.text-center
            th(style="width: 10%" role="button" @click="setSort('id')") ID
              font-awesome-icon.mx-2(:icon="sortField === 'id' ? (sortOrder === 'asc' ? 'sort-up' : 'sort-down') : 'sort'" class="sort-icon mr-auto")
            th(style="width: 25%" role="button" @click="setSort('prenom')") Prénom
              font-awesome-icon.mx-2(:icon="sortField === 'prenom' ? (sortOrder === 'asc' ? 'sort-up' : 'sort-down') : 'sort'" class="sort-icon mr-auto")
            th(style="width: 35%" role="button" @click="setSort('nom')") Nom
              font-awesome-icon.mx-2(:icon="sortField === 'nom' ? (sortOrder === 'asc' ? 'sort-up' : 'sort-down') : 'sort'" class="sort-icon mr-auto")
            th(style="width: 15%" role="button" @click="setSort('id-ref')") ID Ref
              font-awesome-icon.mx-2(:icon="sortField === 'id-ref' ? (sortOrder === 'asc' ? 'sort-up' : 'sort-down') : 'sort'" class="sort-icon mr-auto")
            th(style="width: 10%") Ouvrages
            th(style="width: 10%") Recensions
            th(style="width: 15%") Rec. sur ouvrages

        tbody
          tr(v-if="filteredAuteurs.length === 0")
            td.text-center(colspan=7) Aucun auteur trouvé
          tr.text-center(v-for="auteur in filteredAuteurs" :key="auteur.id" @click="handleAuteurClick(auteur.id)" role="button")
            td {{ auteur.id }}
            td {{ auteur.prenom }}
            td {{ auteur.nom }}
            td {{ auteur['id_ref'] }}
            td {{ auteur['auteur_ouvrages']?.length || 0 }}
            td {{ auteur['auteur_recensions']?.length || 0 }}
            td {{ auteur.nb_recensions_sur_ouvrages || 0 }}

  //- Cartes mobile
  div.d-md-none
    div(v-if="filteredAuteurs.length === 0").text-center.mt-3 Aucun auteur trouvé
    div(v-else v-for="auteur in filteredAuteurs" :key="auteur.id" class="card mb-2" @click="handleAuteurClick(auteur.id)" role="button")
      div.card-body
        h5.card-title.mb-1 {{ auteur.prenom }} {{ auteur.nom }}
        p.mb-1 ID : {{ auteur.id }}
        p.mb-1 ID Ref : {{ auteur.id_ref }}
        p.mb-1 Ouvrages : {{ auteur['auteur_ouvrages']?.length || 0 }}
        p.mb-1 Recensions : {{ auteur['auteur_recensions']?.length || 0 }}
        p.mb-0 Rec. sur ouvrages : {{ auteur.nb_recensions_sur_ouvrages || 0 }}

  //- PAGINATION
  div.d-flex.justify-content-center.mt-3(v-if="totalItems > 0")
    pagination(
      :options="{ hideCount: true }"
      v-model="currentPage"
      :records="totalItems"
      :per-page="limit"
      @paginate="searchAuteurs"
    )
</template>


<style scoped>
.pagination {
  cursor: default;
  font-weight: bold;
  color: #aaa;
}

.page-link {
  color: #4F7878;
}

.page-item.active .page-link {
  background-color: #4F7878;
  border-color: #4F7878;
  color: white;
}

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