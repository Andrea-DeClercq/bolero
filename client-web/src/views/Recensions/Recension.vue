<script setup>
import { inject, ref, onMounted } from "vue";
import { useRoute } from "vue-router";
import ConfirmDeleteModal from "@/components/ConfirmDeleteModal.vue";

// Dépendances
const $api = inject('$api');
const navigation = inject('navigation');
const authStore = inject('authStore');
const { error, hasError, handleError } = inject('errorHandler');
const { notify } = inject('notification')
const route = useRoute();


// Variables
const recension = ref(null);
const isLoading = ref(true);

const idRecension = parseInt(route.params.id);
const showDeleteModal = ref(false);

const deleteRecension = async () => {
  try {
    await $api.recension.deleteRecension(idRecension, authStore.getToken());
    notify("Recension supprimée avec succès.", "success");
    navigation.goToSearchRecension();
  } catch (error) {
    handleError(error, "Erreur lors de la suppression de la recension.");
  }
};

const fetchRecensionDetails = async () => {
  try {
    const response = await $api.recension.getRecensionDetails(idRecension);
    recension.value = response.data;
  } catch (error) {
    handleError(error, "Erreur lors du chargement des données");
  } finally {
    isLoading.value = false;
  }
};

onMounted(() => {
  fetchRecensionDetails();
});
</script>

<template lang="pug">
div.container
  div.text-center(v-if="isLoading")
    h3.d-inline-block.me-3 Chargement
    font-awesome-icon(icon="spinner" spin size="2x")

  div(v-else-if="!hasError.value")
    div.d-flex.flex-column.flex-md-row.justify-content-between.align-items-center.mb-4
      h1.text-center.text-md-start.mb-3.mb-md-0 Détails de la recension

      div.gap-y-2(v-if="authStore.isAuthenticated")
        button.btn.btn-warning.me-2(@click="navigation.goToEditRecension(idRecension)")
          font-awesome-icon(icon="edit")
          span.p-2 Modifier la recension
        button.btn.btn-danger(@click="showDeleteModal = true")
          font-awesome-icon(icon="trash-alt")
          span.px-1 Supprimer la recension

    div.card.mb-4
      div.card-header.text-center.bg-primary.text-white Informations sur la recension
      div.card-body
        ul.list-group.list-group-flush
          li.list-group-item
            strong Titre : 
            p.d-inline-block.px-1(v-html="recension.titre")
          li.list-group-item(v-if="recension['sous_titre']")
            strong Sous-titre : 
            p.d-inline-block(v-html="recension['sous_titre']")
          li.list-group-item
            strong Titre de la revue : 
            p.d-inline-block.px-1 {{ recension['titre_revue'] || 'Non spécifié' }}
          li.list-group-item(v-if="recension.doi")
            strong DOI : 
            | {{ recension.doi }}
          li.list-group-item
            strong Langue : 
            | {{ recension.langue || 'Non spécifiée' }}
          li.list-group-item
            strong Année de publication : 
            | {{ recension.annee || 'Non spécifiée' }}
          li.list-group-item(v-if="recension.volume")
            strong Volume : 
            | {{ recension.volume }}
          li.list-group-item(v-if="recension.numero")
            strong Numéro : 
            | {{ recension.numero }}
          li.list-group-item
            strong Portail : 
            | {{ recension.portail || 'Non spécifié' }}
          li.list-group-item(v-if="recension.url")
            strong URL : 
            span.text-decoration-none.text-primary(
              @click="navigation.redirectToExternalUrl(recension.url)"
              role="button"
            )
              div.d-inline-block
                p
                  | Redirection vers la recension
                  font-awesome-icon.ms-2.text-primary.cursor-pointer(
                    :icon="'external-link-alt'"
                  )

    div(v-if="recension['recension_auteurs']?.length > 0")
      h3.text-center.text-muted.mt-4 Auteur(s)
      ul.list-group
        li.list-group-item.list-group-item-action.d-flex.justify-content-between.align-items-center(
          v-for="auteur in recension['recension_auteurs']"
          :key="auteur.auteur.id"
          @click="navigation.goToAuteur(auteur.auteur.id)"
          role="button"
        )
          div
            strong {{ auteur.auteur.prenom }} {{ auteur.auteur.nom }}

    div(v-if="recension['recension_ouvrages']?.length > 0")
      h3.text-center.text-muted.mt-4 Ouvrage cible de la recension
      ul.list-group
        li.list-group-item.list-group-item-action.d-flex.justify-content-between.align-items-center(
          v-for="ouvrage in recension['recension_ouvrages']"
          :key="ouvrage.ouvrage.id"
          @click="navigation.goToOuvrage(ouvrage.ouvrage.id)"
          role="button"
        )
          div.row
            span(v-html="ouvrage.ouvrage.titre")
            span {{ ouvrage.ouvrage.editeur }} ({{ ouvrage.ouvrage.annee_parution }})

ConfirmDeleteModal(
  :visible="showDeleteModal"
  title="Supprimer la recension"
  message="Cette action supprimera également toutes les relations associées à cette recension. Voulez-vous continuer ?"
  @confirm="deleteRecension"
  @cancel="showDeleteModal = false"
)
</template>

<style scoped>
.v-collapse {
  transition: height 600ms ease-in-out;
}
</style>
