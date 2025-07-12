<script setup>
import { ref, inject, computed } from "vue";
import { useRoute } from 'vue-router';
import { hydrateFields, generateId, normalizeOuvrage } from '@/constants/utils.js'
import AuteurSelectorModal from "@/components/Auteur/AuteurSelectorModal.vue";
import EditeurSelectorModal from "@/components/Editeur/EditeurSelectorModal.vue";
import LangageSelector from "@/components/LangageSelector.vue";

// Dépendances
const emits = defineEmits(['ouvrageCreated']);
const $api = inject('$api');
const navigation = inject('navigation');
const authStore = inject('authStore');
const { hasError, handleError } = inject('errorHandler');
const { notify } = inject('notification');
const route = useRoute();

const isModal = ref(!['ouvrage-new', 'ouvrage-edit'].includes(route.name));
const id = ref(
  !isModal.value && route.params.id ? parseInt(route.params.id) : null);
const isEditing = ref(!!id.value);
const ouvrage = ref(null);

// Champs du formulaire
const idProprio = ref(`${authStore.getUserPortailId().toUpperCase()}_`);
const titre = ref("");
const sousTitre = ref("");
const traduitPar = ref("");
const editeur = ref("");
const volume = ref("");
const anneeParution = ref("");
const ean = ref("");
const doi = ref("");
const langue = ref("fr");
const portail = ref(authStore.getUserPortailId());
const url = ref("");

if (!isEditing.value) {
  idProprio.value += generateId()
}

const fieldsMapping = new Map([
  [idProprio, 'id_proprio'],
  [titre, 'titre'],
  [sousTitre, 'sous_titre'],
  [traduitPar, 'traduit_par'],
  [editeur, 'editeur'],
  [volume, 'volume'],
  [anneeParution, 'annee_parution'],
  [ean, 'ean'],
  [doi, 'doi'],
  [langue, 'langue'],
  [portail, 'portail'],
  [url, 'url']
])

const loading = ref(false);
const showAdditionalFields = ref(isEditing.value ? true : false);

const originalAuthors = ref([]);
const selectedAuthors = ref([]);
const showAuthorModal = ref(false);
const showEditeurModal = ref(false);
const selectedEditeur = ref(null);
const idRelationToDelete = ref([]);

const removeAuthor = (author) => {
  const existingRelation = originalAuthors.value.find(a => a.id === author.id);
  if (isEditing.value && existingRelation?.idRelation) {
    idRelationToDelete.value.push(existingRelation.idRelation); // Stocker l'ID de la relation pour suppression
  }
  selectedAuthors.value = selectedAuthors.value.filter(a => a.id !== author.id);
};

const updateEditeur = (ed) => {
  selectedEditeur.value = ed;
  editeur.value = ed.nom;
};

const fetchOuvrage = async () => {
  try {
    const response = await $api.ouvrage.getOuvrageDetails(id.value);
    ouvrage.value = response.data;

    // Remplir les champs    
    hydrateFields(ouvrage.value, fieldsMapping)
    originalAuthors.value = ouvrage.value.ouvrage_auteurs?.map(a => ({
      id: a.auteur.id,
      idRelation: a.id_relation,
      idRef: a.auteur.id_ref,
      nom: a.auteur.nom,
      prenom: a.auteur.prenom
    })) || [];

    selectedAuthors.value = [...originalAuthors.value];
    if (ouvrage.value.editeur) {
      selectedEditeur.value = {
        nom: ouvrage.value.editeur
      };
    }

  } catch (err) {
    handleError(err, 'Erreur lors du chargement de l’ouvrage à éditer');
  }
};

if (isEditing.value) {
  fetchOuvrage();
}

const submitOuvrage = async () => {
  const payload = {
      id_proprio: idProprio.value || null,
      titre: titre.value,
      "sous_titre": sousTitre.value || null,
      traduit_par: traduitPar.value || null,
      editeur: editeur.value,
      volume: volume.value || null,
      "annee_parution": anneeParution.value,
      ean: ean.value || null,
      doi: doi.value || null,
      langue: langue.value,
      portail: portail.value || null,
      url: url.value || null,
    };

  // On oblige un auteur au moins sur l'ouvrage
  if (!titre.value || !editeur.value || !anneeParution.value || !ean.value || selectedAuthors.value.length === 0) {
    handleError("Veuillez remplir les champs obligatoires (incluant l'EAN) et sélectionner au moins un auteur.");
    return;
  }

  loading.value = true;
  try {
    const response = isEditing.value
      ? await $api.ouvrage.putOuvrage(id.value, authStore.getToken(), payload)
      : await $api.ouvrage.postOuvrage(authStore.getToken(), payload);

    if (![200, 201].includes(response.status)) {
      throw new Error("Réponse inattendue de l'API");
    }

    const idOuvrage = response.data.id || id.value;
    
    if (isEditing.value && idRelationToDelete.value.length > 0) {
      await $api.relation.deleteAuthorBookRelationsBatch(
        authStore.getToken(),
        idRelationToDelete.value
      );
    }

    const newRelations = selectedAuthors.value
      .filter((author) => !author.idRelation)
      .map((author) => ({
        id_ouvrage: idOuvrage,
        id_auteur: author.id,
      }));

    if (newRelations.length > 0) {
      await $api.relation.postRelationsBatch(authStore.getToken(), newRelations);
    }

    if (!hasError.value) {
      notify(
        isEditing.value
          ? "Ouvrage mis à jour avec succès"
          : "Ouvrage crée avec succès", 
        "success"
      );

      if (isModal.value) {
        const newOuvrage = normalizeOuvrage({
          ...payload,
          id: response.data.id,
        })
        emits('ouvrageCreated', newOuvrage);
      } else {
        setTimeout(() => {
          if (isEditing.value) {
            navigation.goToOuvrage(idOuvrage);
          } else {
            navigation.goToSearchOuvrage();
          }
        }, 1500);
      }
    }
  } catch (error) {
    handleError(error, "Erreur lors de l'enregistrement de l'ouvrage");
  } finally {
    loading.value = false;
  }
};
</script>

<template lang="pug">
  div.container.mt-4
    div.position-relative.mb-4
      button.btn.btn-secondary.position-absolute.start-0(
          v-if="isEditing && !isModal", @click="navigation.goToOuvrage(id.value)"
        )
        font-awesome-icon(icon="arrow-left")
        span.px-1 Retour à la fiche ouvrage

      h2.text-center {{ isEditing ? "Mise à jour de l'ouvrage" : "Créer un ouvrage" }}
  
      form(@submit.prevent="submitOuvrage")
        h6.border-secondary.border-bottom.text-center.text-muted.p-1.mt-4.mb-2 Informations principales
        .row.mb-3
          .col
            label.form-label Titre *
            input.form-control(v-model="titre" required)
        .row.mb-3
          .col-4
            .label.form-label Éditeur *
            .input-group
              input.form-control(:value="selectedEditeur?.nom || ''" readonly)
              button.btn.btn-secondary(type="button" @click="showEditeurModal = true") Choisir
          .col-4
            label.form-label EAN *
            input.form-control(v-model="ean" required)
          .col-4
            label.form-label Année de parution *
            input.form-control(type="number" v-model="anneeParution" min=0 required)

        .d-flex.justify-content-center.align-items-center.border-secondary.border-bottom.text-muted.mt-4.mb-2(type="button" @click="showAdditionalFields = !showAdditionalFields")
          h6.text-center.p-1.mb-0 Informations complémentaires
          font-awesome-icon.ml-2(:icon="showAdditionalFields ? 'chevron-up' : 'chevron-down'")
        collapse(:when="showAdditionalFields" class="v-collapse")
          .row.mb-3
            .col
              label.form-label Sous-titre
              input.form-control(v-model="sousTitre")
            .col
              label.form-label Volume
              input.form-control(v-model="volume")

          .row.mb-3
            .col
              label.form-label Traduit par
              input.form-control(v-model="traduitPar")
            .col
              label.form-label Langue
              LangageSelector(v-model="langue")

          h6.border-secondary.border-bottom.text-center.text-muted.p-1.mt-4.mb-2  Identifiants & portail
            .row.mb-3
              .col
                label.form-label URL
                input.form-control(v-model="url")
              .col
                label.form-label DOI
                input.form-control(v-model="doi")

            .row.mb-3
              .col
                label.form-label Portail
                input.form-control(v-model="portail")
              .col
                label.form-label ID Propriétaire
                input.form-control(v-model="idProprio")

        h6.border-secondary.border-bottom.text-center.text-muted.p-1.mt-4.mb-2 Associer un ou plusieurs auteurs
        div.text-center.my-2
          button.btn.btn-outline-primary(type="button" @click="showAuthorModal = true")
            font-awesome-icon(icon="user-plus")
            |  Ajouter un auteur

        ul.list-group.mb-3(v-if="selectedAuthors.length")
          li.list-group-item.d-flex.justify-content-between.align-items-center(
            v-for="author in selectedAuthors"
            :key="author.id"
          )
            | {{ author.nom }} {{ author.prenom }}
            button.btn.btn-sm.btn-danger(
              type="button"
              @click="isEditing ? removeAuthor(author) : selectedAuthors.splice(index, 1)"
            )
              font-awesome-icon(icon="trash-can")

        div.text-center.mt-4
          button.btn.btn-primary(type="submit" :disabled="loading")
            span(v-if="loading") Traitement en cours...
            span(v-else) {{ isEditing ? "Mettre à jour l'ouvrage" : "Créer l'ouvrage" }}

  AuteurSelectorModal(
        v-if="showAuthorModal"
        :selectedAuthors="selectedAuthors"
        @update:selectedAuthors="selectedAuthors = $event"
        @close="showAuthorModal = false"
      )

  EditeurSelectorModal(
    v-if="showEditeurModal"
    :selectedEditeur="selectedEditeur"
    @update:selectedEditeur="updateEditeur"
    @close="showEditeurModal = false"
  )

</template>