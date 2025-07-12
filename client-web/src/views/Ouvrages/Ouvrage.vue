<script setup>
import { inject, ref, computed, onMounted } from 'vue';
import { useRoute } from 'vue-router';
import ConfirmDeleteModal from "@/components/ConfirmDeleteModal.vue";

// Dépendances
const $api = inject('$api');
const navigation = inject('navigation');
const authStore = inject('authStore');
const { error, hasError, handleError } = inject('errorHandler');
const { notify } = inject('notification')
const route = useRoute();

// Variables
const ouvrage = ref(null);
const isLoading = ref(true);

const hasAuteurs = computed(() => ouvrage.value?.['ouvrage_auteurs']?.length > 0);
const hasRecensions = computed(() => ouvrage.value?.['ouvrage_recensions']?.length > 0);

const idOuvrage = parseInt(route.params.id);
const recensionsAssocies = ref([])
const showDeleteModal = ref(false);

const deleteOuvrage = async () => {
  try {
    await $api.ouvrage.deleteOuvrage(idOuvrage, authStore.getToken());
    notify("L'ouvrage a bien été supprimé.", "success");
    navigation.goToSearchOuvrage();
  } catch (error) {
    handleError(error, "Erreur lors de la suppression de l'ouvrage.");
  }
};

const fetchOuvrageDetails = async () => {
  try {
    const response = await $api.ouvrage.getOuvrageDetails(idOuvrage);
    ouvrage.value = response.data;
    // Mapping des recensions pour avoir un delete dynamique 
    recensionsAssocies.value = ouvrage?.value["ouvrage_recensions"]?.map(r => ({
      id: r.recension.id,
      idRelation: r["id_relation"],
      titre: r.recension.titre,
      annee: r.recension.annee,
      titre_revue: r.recension["titre_revue"],
      url: r.recension.url,
    })) || [];
  } catch (error) {
    handleError(error, "Erreur lors du chargement des données");
  } finally {
    isLoading.value = false;
  }
};

const deleteRelationRecension = async (idRelation) => {
  const result = confirm(`Êtes-vous sûr de vouloir supprimer l'association avec cette recension ?`);
  if (result) {
    try {
      await $api.relation.deleteBookReviewRelation(idRelation, authStore.getToken());
      recensionsAssocies.value = recensionsAssocies.value.filter(r => r.idRelation !== idRelation);
      notify("L'association avec cette recension a bien été supprimée.", "success");
    } catch (error) {
      handleError(error, "Erreur lors de la suppression de l'association");
    }
  }
}


onMounted(() => {
  fetchOuvrageDetails();
})
</script>

<template lang="pug">
div.container
  div.text-center(v-if="isLoading")
    h3.d-inline-block.me-3 Chargement
    font-awesome-icon(icon="spinner" spin size="2x")
  
  div(v-else-if="!hasError.value")
    div.position-relative.mb-4
      div.position-absolute.end-0.py-1(v-if="authStore.isAuthenticated")
        button.btn.btn-warning.mx-2(@click="navigation.goToEditOuvrage(idOuvrage)")
          font-awesome-icon(icon="edit")
          span.p-2 Modifier l'ouvrage
        button.btn.btn-danger(@click="showDeleteModal = true")
          font-awesome-icon(icon="trash-alt")
          span.px-1 Supprimer l'ouvrage
      h1.text-center Détails de l'ouvrage
    
    div.card.mb-4
      div.card-header.text-center.bg-primary.text-white Informations sur l'ouvrage
      div.card-body
        ul.list-group.list-group-flush
          li.list-group-item
            strong Titre :
            p.d-inline-block.px-1(v-html="ouvrage.titre")
          li.list-group-item(v-if="ouvrage['sous_titre']")
            strong Sous-titre : 
            p.d-inline-block.px-1(v-html="ouvrage['sous_titre']")
          li.list-group-item
            strong Éditeur : 
            | {{ ouvrage.editeur }}
          li.list-group-item
            strong Année de parution : 
            | {{ ouvrage['annee_parution'] }}
          li.list-group-item(v-if="ouvrage.ean")
            strong EAN : 
            | {{ ouvrage.ean }}
          li.list-group-item(v-if="ouvrage.doi")
            strong DOI : 
            | {{ ouvrage.doi }}
          li.list-group-item
            strong Portail : 
            | {{ ouvrage.portail }}
          li.list-group-item
            strong Langue : 
            | {{ ouvrage.langue.toUpperCase() }}
          li.list-group-item(v-if="ouvrage.url")
            strong URL : 
            span.text-decoration-none.text-primary(
              @click="navigation.redirectToExternalUrl(ouvrage.url)"
              role="button"
            )
              div.d-inline-block
                p
                  | Redirection vers l'ouvrage
                  font-awesome-icon.ms-2.text-primary.cursor-pointer(
                    :icon="'external-link-alt'"
                  )

    div(v-if="hasAuteurs")
      h3.text-center.text-muted.mt-4 Auteur(s)
      ul.list-group
        li.list-group-item.list-group-item-action.d-flex.justify-content-between.align-items-center(
          v-for="auteur in ouvrage['ouvrage_auteurs']"
          :key="auteur.auteur.id"
          @click="navigation.goToAuteur(auteur.auteur.id)"
          role="button"
        )
          div
            strong {{ auteur.auteur.prenom }} {{ auteur.auteur.nom }}

    div(v-if="hasRecensions")
      h3.text-center.text-muted.mt-4 Recension(s) sur l'ouvrage
      ul.list-group
        li.list-group-item.list-group-item-action.d-flex.justify-content-between.align-items-center(
          v-for="recension in recensionsAssocies"
          :key="recension.id"
          @click="navigation.goToRecension(recension.id)"
          role="button"
        )
          div.d-flex.flex-column
            span(v-html="recension.titre")
            div.d-flex
              span.d-inline-block.me-2(v-html="recension['titre_revue']") 
              span.d-inline-block ({{ recension.annee }})
          div
            font-awesome-icon.text-primary.cursor-pointer(
              :icon="'external-link-alt'"
              @click.stop="navigation.redirectToExternalUrl(recension.url)"
            )
            font-awesome-icon.text-danger.cursor-pointer.px-3(
              :icon="'trash-can'"
              @click.stop="deleteRelationRecension(recension.idRelation)"
            )(v-if="authStore.isAuthenticated")

ConfirmDeleteModal(
  :visible="showDeleteModal"
  title="Supprimer l'ouvrage"
  message="Cette action supprimera également toutes les relations associées à cet ouvrage. Voulez-vous continuer ?"
  @confirm="deleteOuvrage"
  @cancel="showDeleteModal = false"
)
</template>