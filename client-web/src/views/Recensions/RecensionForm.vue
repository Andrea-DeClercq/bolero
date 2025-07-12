<script setup>
import { ref, inject, computed } from "vue";
import { useRoute } from 'vue-router';
import { hydrateFields, generateId } from "@/constants/utils";
import AuteurSelectorModal from "@/components/Auteur/AuteurSelectorModal.vue";
import LangageSelector from "@/components/LangageSelector.vue";
import OuvrageSelectorModal from "@/components/Ouvrage/OuvrageSelectorModal.vue";
import RevueSelectorModal from "@/components/Revue/RevueSelectorModal.vue";

// Dépendances
const $api = inject("$api");
const navigation = inject("navigation");
const authStore = inject("authStore");
const { hasError, handleError } = inject('errorHandler');
const { notify } = inject('notification');
const route = useRoute();

const id = ref(route.params.id ? parseInt(route.params.id) : null);
const isEditing = computed(() => !!id.value);
const recension = ref(null);

// Champs du formulaire
const idProprio = ref(`${authStore.getUserPortailId().toUpperCase()}_`);
const titre = ref("");
const sousTitre = ref("");
const portail = ref(authStore.getUserPortailId());
const traduitPar = ref("");
const langue = ref("fr");
const titreRevue = ref("");
const annee = ref("");
const volume = ref("");
const numero = ref("");
const dateParution = ref("");
const doi = ref("");
const url = ref("")

if (!isEditing.value) {
  idProprio.value += generateId();
}

const fieldsMapping = new Map([
  [idProprio, 'id_proprio'],
  [titre, 'titre'],
  [sousTitre, 'sous_titre'],
  [portail, 'portail'],
  [traduitPar, 'traduit_par'],
  [langue, 'langue'],
  [titreRevue, 'titre_revue'],
  [annee, 'annee'],
  [volume, 'volume'],
  [numero, 'numero'],
  [dateParution, 'date_parution'],
  [doi, 'doi'],
  [url, 'url'],
]);

const originalAuthors = ref([]);
const selectedAuthors = ref([]);
const originalBooks = ref([])
const selectedBooks = ref([])
const idAuthorRelationToDelete = ref([]);
const idBookRelationToDelete = ref([])
const showAuthorModal = ref(false);
const showOuvrageModal = ref(false);
const showRevueModal = ref(false);
const selectedRevue = ref(null);
const loading = ref(false);
const showAdditionalFields = ref(isEditing.value ? true : false);

const removeAuthor = (author) => {
  const existingRelation = originalAuthors.value.find(a => a.id === author.id);
  if (isEditing.value && existingRelation?.idRelation) {
    idAuthorRelationToDelete.value.push(existingRelation.idRelation);
  }
  selectedAuthors.value = selectedAuthors.value.filter(a => a.id !== author.id);
};

const removeBook = (book) => {
  const existingRelation = originalBooks.value.find(b => b.id === book.id);
  if (isEditing.value && existingRelation?.idRelation) {
    idBookRelationToDelete.value.push(existingRelation.idRelation);
  }
  selectedBooks.value = selectedBooks.value.filter(b => b.id !== book.id);
}

const updateRevue = (r) => {
  selectedRevue.value = r;
  titreRevue.value = r.titre;
}

const fetchRecension = async () => {
  try {
    const response = await $api.recension.getRecensionDetails(id.value);
    recension.value = response.data;

    hydrateFields(recension.value, fieldsMapping);

    originalAuthors.value = recension.value.recension_auteurs?.map(a => ({
      id: a.auteur.id,
      idRelation: a.id_relation,
      idRef: a.auteur.id_ref,
      nom: a.auteur.nom,
      prenom: a.auteur.prenom,
    })) || [];

    originalBooks.value = recension.value.recension_ouvrages?.map(o => ({
      id: o.ouvrage.id,
      idRelation: o.id_relation,
      titre: o.ouvrage.titre,
      sousTitre: o.ouvrage.sous_titre,
      editeur: o.ouvrage.editeur,
      anneeParution : o.ouvrage.annee_parution,
    })) || [];

    selectedAuthors.value = [...originalAuthors.value];
    selectedBooks.value = [...originalBooks.value];
    if (recension.value.titre_revue) {
      selectedRevue.value = {
        titre: recension.value.titre_revue
      }
    }
  } catch (err) {
    handleError(err, 'Erreur lors du chargement de la recension à éditer');
  }
};

if (isEditing.value) {
  fetchRecension();
}

const submitRecension = async () => {

  if (selectedAuthors.value.length === 0) {
    handleError("Une recension doit être associée à au moins un auteur.");
    return;
  }

  if (selectedBooks.value.length === 0) {
    handleError("Une recension doit être associée à un ouvrage.");
    return;
  }

  if (!selectedRevue.value) {
    handleError("Un titre de revue doit être sélectionné.")
    return;
  }

  const payload = {
    id_proprio: idProprio.value || null,
    titre: titre.value || null,
    sous_titre: sousTitre.value || null,
    portail: portail.value || null,
    traduit_par: traduitPar.value || null,
    langue: langue.value || null,
    titre_revue: titreRevue.value || null,
    annee: annee.value || null,
    volume: volume.value || null,
    numero: numero.value || null,
    date_parution: dateParution.value || null,
    doi: doi.value || null,
    url: url.value || null
  };

  loading.value = true;
  try {
    const response = isEditing.value
      ? await $api.recension.putRecension(id.value, authStore.getToken(), payload)
      : await $api.recension.postRecension(authStore.getToken(), payload);

    if (![200, 201].includes(response.status)) {
      throw new Error("Réponse inattendue de l'API");
    }

    const idRecension = response.data.id || id.value;

    // Utilisations des endpoints batch pour éviter de surcharger la session SQLAlchemy côté back
    // Delete les relations auteurs
    if (isEditing.value && idAuthorRelationToDelete.value.length > 0) {
      await $api.relation.deleteAuthorReviewRelationsBatch(
        authStore.getToken(),
        idAuthorRelationToDelete.value
      );
    }

    // Delete les relations ouvrages
    if (isEditing.value && idBookRelationToDelete.value.length > 0) {
      await $api.relation.deleteBookReviewRelationsBatch(
        authStore.getToken(),
        idBookRelationToDelete.value
      );
    }

    // Ajoute la liste de relations à la recension
    const newRelations = [
      ...selectedAuthors.value
        .filter(author => !author.idRelation)
        .map(author => ({ id_recension: idRecension, id_auteur: author.id })),

      ...selectedBooks.value
        .filter(book => !book.idRelation)
        .map(book => ({ id_recension: idRecension, id_ouvrage: book.id })),
    ];

    if (newRelations.length > 0) {
      await $api.relation.postRelationsBatch(authStore.getToken(), newRelations);
    }

    if (!hasError.value) {
      notify(
        isEditing.value
          ? "Recension mise à jour avec succès"
          : "Recension ajoutée avec succès",
        "success"
      );

      setTimeout(() => {
        if (isEditing.value) {
          navigation.goToRecension(idRecension);
        } else {
          navigation.goToSearchRecension();
        }
      }, 1500);
    }
  } catch (error) {
    handleError(error, "Erreur lors de l'enregistrement de la recension");
  } finally {
    loading.value = false;
  }
};
</script>

<template lang="pug">
  div.container.mt-4
    div.position-relative.mb-4
      button.btn.btn-secondary.position-absolute.start-0(v-if="isEditing", @click="navigation.goToRecension(id.value)")
        font-awesome-icon(icon="arrow-left")
        span.px-1 Retour à la fiche recension

    h2.text-center {{ isEditing ? "Mise à jour de la recension" : "Ajouter une recension" }}

    form(@submit.prevent="submitRecension")
      h6.border-secondary.border-bottom.text-center.text-muted.p-1.mt-4.mb-2 Informations principales
      .row.mb-3
        .col
          label.form-label Titre *
          input.form-control(v-model="titre" required)
        .col
          label.form-label Titre de la revue *
          .input-group
            input.form-control(:value="selectedRevue?.titre || ''" readonly)
            button.btn.btn-secondary(type="button" @click="showRevueModal = true") Choisir
        .col-3
          label.form-label Année *
          input.form-control(type="number" v-model="annee" required)

      .row.mb-3
        .col
          label.form-label URL *
          input.form-control(v-model="url")

      h6.border-secondary.border-bottom.text-center.text-muted.p-1.mt-4.mb-2 Associer auteurs & ouvrages
      .row
        .col
          div.text-center.my-2
            button.btn.btn-outline-primary(type="button" @click="showAuthorModal = true")
              font-awesome-icon(icon="user-plus")
              |  Ajouter un auteur
          ul.list-group.mb-3(v-if="selectedAuthors.length")
            li.list-group-item.d-flex.justify-content-between.align-items-center(v-for="author in selectedAuthors" :key="author.id")
              | {{ author.nom }} {{ author.prenom }}
              button.btn.btn-sm.btn-danger(type="button" @click="isEditing ? removeAuthor(author) : selectedAuthors.splice(index, 1)")
                font-awesome-icon(icon="trash-can")

        .col
          div.text-center.my-2
            button.btn.btn-outline-primary(type="button" @click="showOuvrageModal = true")
              font-awesome-icon(icon="book")
              |  Associer un ouvrage
          ul.list-group.mb-3(v-if="selectedBooks.length")
            li.list-group-item.d-flex.justify-content-between.align-items-center(v-for="book in selectedBooks" :key="book.id")
              div
                span(v-html="book.titre").px-1
                span(v-if="book.sousTitre") - 
                  span(v-html="book.sousTitre").px-1
                span {{ book.editeur }} ({{book.anneeParution}})
              button.btn.btn-sm.btn-danger(type="button" @click="isEditing ? removeBook(book) : selectedBooks.splice(index, 1)")
                font-awesome-icon(icon="trash-can")

      .d-flex.justify-content-center.align-items-center.border-secondary.border-bottom.text-muted.mt-4.mb-2(type="button" @click="showAdditionalFields = !showAdditionalFields")
        h6.text-center.p-1.mb-0 Informations complémentaires
        font-awesome-icon.ml-2(:icon="showAdditionalFields ? 'chevron-up' : 'chevron-down'")
      collapse(:when="showAdditionalFields" class="v-collapse")
        .row.mb-3
          .col
            label.form-label Sous-titre
            input.form-control(v-model="sousTitre")
          .col-4
            label.form-label Traduit par
            input.form-control(v-model="traduitPar" placeholder="Nom Prénom")
          .col-3
            label.form-label Langue
            LangageSelector(v-model="langue")

        .row.mb-3
          .col-3
            label.form-label Volume
            input.form-control(v-model="volume")
          .col-3
            label.form-label Numéro
            input.form-control(v-model="numero")
          .col-3
            label.form-label Date de parution
            input.form-control(type="date" v-model="dateParution")

        .row.mb-3
          .col
            label.form-label DOI
            input.form-control(v-model="doi")
          .col-3
            label.form-label Portail
            input.form-control(v-model="portail")
          .col-3
            label.form-label ID Propriétaire
            input.form-control(v-model="idProprio")

      div.text-center.mt-4
        button.btn.btn-primary(type="submit" :disabled="loading")
          span(v-if="loading") Traitement en cours...
          span(v-else) {{ isEditing ? "Mettre à jour la recension" : "Ajouter la recension" }}

    OuvrageSelectorModal(
      v-if="showOuvrageModal"
      :selectedBooks="selectedBooks"
      @update:selectedBooks="selectedBooks = $event"
      @close="showOuvrageModal = false"
    )

    AuteurSelectorModal(
      v-if="showAuthorModal"
      :selectedAuthors="selectedAuthors"
      @update:selectedAuthors="selectedAuthors = $event"
      @close="showAuthorModal = false"
    )

    RevueSelectorModal(
      v-if="showRevueModal"
      :selectedRevue="selectedRevue"
      @update:selectedRevue="updateRevue"
      @close="showRevueModal = false"
    )
</template>