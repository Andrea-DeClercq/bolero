<script setup>
import { inject, ref, computed, onMounted } from 'vue';
import { useRoute } from 'vue-router';
import ConfirmDeleteModal from "@/components/ConfirmDeleteModal.vue";

const $api = inject('$api');
const navigation = inject('navigation');
const authStore = inject('authStore');
const { handleError } = inject('errorHandler');
const { notify } = inject('notification')

const route = useRoute();
const idAuteur = parseInt(route.params.id);

const auteur = ref(null);
const isLoading = ref(true);
const recensionsSurPublications = ref([]);
const hasOuvrages = computed(() => auteur.value?.['auteur_ouvrages']?.length > 0);
const hasRecensions = computed(() => auteur.value?.['auteur_recensions']?.length > 0);
const showOuvrages = ref(true);
const showRecensions = ref(true);
const showRecensionsSurPub = ref(true);
const showDeleteModal = ref(false);

const deleteAuteur = async () => {
  try {
    await $api.auteur.deleteAuteur(idAuteur, authStore.getToken());
    notify("Auteur supprimé avec succès.", "success");
    navigation.goToSearchAuteur();
  } catch (error) {
    handleError(error, "Erreur lors de la suppression de l’auteur.");
  }
};

const fetchAuteurDetails = async () => {
  try {
    const response = await $api.auteur.getAuteurDetails(idAuteur);
    auteur.value = response.data;
$  } catch (error) {
    handleError(error, 'Erreur lors du chargement de l’auteur.');
  } finally {
    isLoading.value = false;
  }
};

const fetchRecensionsSurPublications = async () => {
  try {
    const ouvragesResponse = await $api.ouvrage.getOuvrages({ id_auteur: idAuteur });
    const ouvrages = ouvragesResponse.data.ouvrages || [];
    const recensionsMap = new Map();

    ouvrages.forEach(ouvrage => {
      ouvrage.ouvrage_recensions?.forEach(({ recension }) => {
        if (recension?.id) recensionsMap.set(recension.id, recension);
      });
    });

    if (auteur.value) {
      const { prenom, nom } = auteur.value;
      const recensionsResponse = await $api.recension.getRecensions({ titre: `${prenom} ${nom}` });
      recensionsResponse.data.recension?.forEach(r => recensionsMap.set(r.id, r));
    }

    recensionsSurPublications.value = Array.from(recensionsMap.values());
  } catch (error) {
    handleError(error, 'Erreur lors du chargement des recensions sur les publications.');
  }
};

const titreOuvrages = computed(() =>
  auteur.value?.auteur_ouvrages?.length > 1 ? 'Ouvrages' : 'Ouvrage'
);

const titreRecensions = computed(() =>
  auteur.value?.auteur_recensions?.length > 1 ? 'Recensions écrites' : 'Recension écrite'
);

const titreRecensionsSurPub = computed(() =>
  recensionsSurPublications.value.length > 1
    ? 'Recensions sur les publications de l\'auteur'
    : 'Recension sur la publication de l\'auteur'
);

const deleteRelationOuvrage = async (idRelation) => {
  if (!confirm("Confirmer la suppression de l'association avec cet ouvrage ?")) return;
  try {
    await $api.relation.deleteAuthorBookRelation(idRelation, authStore.getToken());
    auteur.value.auteur_ouvrages = auteur.value.auteur_ouvrages.filter(o => o.id_relation !== idRelation);
    notify('Association avec l’ouvrage supprimée.', 'success');
  } catch (error) {
    handleError(error, 'Erreur lors de la suppression de l’association.');
  }
};

const deleteRelationRecension = async (idRelation) => {
  if (!confirm("Confirmer la suppression de l'association avec cette recension ?")) return;
  try {
    await $api.relation.deleteAuthorReviewRelation(idRelation, authStore.getToken());
    auteur.value.auteur_recensions = auteur.value.auteur_recensions.filter(r => r.id_relation !== idRelation);
    notify('Association avec la recension supprimée.', 'success');
  } catch (error) {
    handleError(error, 'Erreur lors de la suppression de l’association.');
  }
};

onMounted(async () => {
  await fetchAuteurDetails();
  await fetchRecensionsSurPublications();
});
</script>

<template lang="pug">
div.container
  div.text-center(v-if="isLoading")
    h3.d-inline-block.me-3 Chargement
    font-awesome-icon(icon="spinner" spin size="2x")

  div(v-else-if="auteur")
    div.position-relative.mb-4
      div.position-absolute.end-0.py-1(v-if="authStore.isAuthenticated")
        button.btn.btn-warning.mx-2(@click="navigation.goToEditAuteur(idAuteur)")
          font-awesome-icon(icon="edit")
          span.p-1 Modifier l'auteur
        button.btn.btn-danger(@click="showDeleteModal = true")
          font-awesome-icon(icon="trash-alt")
          span.px-1 Supprimer l'auteur
      h1.text-center Détails de l'auteur

    div.card.mb-4
      div.card-header.text-center.bg-primary.text-white Informations sur {{ auteur.nom }} {{ auteur.prenom }}
      div.card-body
        ul.list-group.list-group-flush
          li.list-group-item
            strong Nom :
            span.px-2 {{ auteur.nom }}
          li.list-group-item
            strong Prénom :
            span.px-2 {{ auteur.prenom }}
          li.list-group-item
            strong ID Référence (ID ABES) :
            span.px-2 {{ auteur.id_ref || 'Non renseigné' }}
          li.list-group-item
            strong ID Propriétaire :
            span.px-2 {{ auteur.id_proprio }}

    div.m-4.border-bottom.border-secondary(v-if="recensionsSurPublications.length > 0")
      .d-flex.justify-content-center.align-items-center.text-muted(
        type="button" @click="showRecensionsSurPub = !showRecensionsSurPub"
      )
        h3.text-center {{ titreRecensionsSurPub }}
        font-awesome-icon.p-2.ml-2(:icon="showRecensionsSurPub ? 'chevron-up' : 'chevron-down'")
      collapse(:when="showRecensionsSurPub" class="v-collapse")
        ul.list-group.mb-4
          li.list-group-item.list-group-item-action.d-flex.justify-content-between.align-items-center(
            v-for="recension in recensionsSurPublications"
            :key="recension.id"
            @click="navigation.goToRecension(recension.id)"
            role="button"
          )
            div.d-flex.flex-column
              span(v-html="recension.titre")
              span.text-muted {{ recension.annee }} - {{ recension.titre_revue }}
            font-awesome-icon.text-primary.cursor-pointer(
              :icon="'external-link-alt'"
              @click.stop="navigation.redirectToExternalUrl(recension.url)"
            )

    div.row
      div(:class="hasOuvrages && hasRecensions ? 'col-md-6' : 'col-12'", v-if="hasOuvrages")
        .d-flex.justify-content-center.align-items-center.text-success(type="button" @click="showOuvrages = !showOuvrages") 
          h4.text-center.mb-2 {{ titreOuvrages }} de l'auteur ({{ auteur.auteur_ouvrages.length }})
          font-awesome-icon.p-2.ml-2(:icon="showOuvrages ? 'chevron-up' : 'chevron-down'")
        collapse(:when="showOuvrages" class="v-collapse")
          ul.list-group.mb-4
            li.list-group-item.list-group-item-action.d-flex.justify-content-between.align-items-center(
              v-for="ouvrage in auteur.auteur_ouvrages"
              :key="ouvrage.ouvrage.id"
              @click="navigation.goToOuvrage(ouvrage.ouvrage.id)"
              role="button"
            )
              div.d-flex.flex-column.col-9
                span(v-html="ouvrage.ouvrage.titre")
                span.text-muted {{ ouvrage.ouvrage.editeur }} ({{ ouvrage.ouvrage.annee_parution }})
              div
                font-awesome-icon.text-primary.cursor-pointer(
                  :icon="'external-link-alt'"
                  @click.stop="navigation.redirectToExternalUrl(ouvrage.ouvrage.url)"
                )
                font-awesome-icon.text-danger.cursor-pointer.px-3(
                  :icon="'trash-can'"
                  @click.stop="deleteRelationOuvrage(ouvrage.id_relation)"
                )(v-if="authStore.isAuthenticated")

      div(:class="hasOuvrages && hasRecensions ? 'col-md-6' : 'col-12'", v-if="hasRecensions")
        .d-flex.justify-content-center.align-items-center.text-success(type="button" @click="showRecensions = !showRecensions")
          h4.text-center.mb-2 {{ titreRecensions }} par l'auteur ({{ auteur.auteur_recensions.length }})
          font-awesome-icon.p-2.ml-2(:icon="showRecensions ? 'chevron-up' : 'chevron-down'")
        collapse(:when="showRecensions" class="v-collapse")
          ul.list-group.mb-4
            li.list-group-item.list-group-item-action.d-flex.justify-content-between.align-items-center(
              v-for="recension in auteur.auteur_recensions"
              :key="recension.recension.id"
              @click="navigation.goToRecension(recension.recension.id)"
              role="button"
            )
              div.d-flex.flex-column.col-9
                span(v-html="recension.recension.titre")
                span.text-muted {{ recension.recension.annee }} - {{ recension.recension.titre_revue }}
              div
                font-awesome-icon.text-primary.cursor-pointer(
                  :icon="'external-link-alt'"
                  @click.stop="navigation.redirectToExternalUrl(recension.recension.url)"
                )
                font-awesome-icon.text-danger.cursor-pointer.px-3(
                  :icon="'trash-can'"
                  @click.stop="deleteRelationRecension(recension.id_relation)"
                )(v-if="authStore.isAuthenticated")
ConfirmDeleteModal(
  :visible="showDeleteModal"
  title="Supprimer l’auteur"
  message="Cette action supprimera également toutes les relations associées à cet auteur. Voulez-vous continuer ?"
  @confirm="deleteAuteur"
  @cancel="showDeleteModal = false"
)

</template>