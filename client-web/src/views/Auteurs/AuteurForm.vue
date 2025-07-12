<script setup>
import { ref, defineEmits, inject, onMounted } from 'vue';
import { useRoute } from 'vue-router';
import { generateId } from '@/constants/utils';

const emits = defineEmits(['auteurCreated']);
const $api = inject('$api');
const authStore = inject('authStore');
const navigation = inject('navigation');
const { notify } = inject('notification');
const { handleError } = inject('errorHandler');

const route = useRoute();

const isModal = ref(!['auteur-new', 'auteur-edit'].includes(route.name));
const id = ref(
  !isModal.value && route.params.id ? parseInt(route.params.id) : null
);
const isEditing = ref(!!id.value);

const nom = ref('');
const prenom = ref('');
const idRef = ref('');
const idProprio = ref(`${authStore.getUserPortailId().toUpperCase()}_${generateId()}`);
const loading = ref(false);

const fetchAuteur = async () => {
  try {
    const response = await $api.auteur.getAuteurs({ id: id.value });
    if (response.status === 200 && response.data.auteurs.length > 0) {
      const auteur = response.data.auteurs[0];
      nom.value = auteur.nom;
      prenom.value = auteur.prenom;
      idRef.value = auteur.id_ref || '';
      idProprio.value = auteur.id_proprio;
    }
  } catch (error) {
    handleError(error, 'Erreur lors du chargement de l’auteur.');
  }
};

if (isEditing.value) {
  onMounted(() => {
    fetchAuteur();
  });
}

const submit = async () => {
  if (!nom.value || !prenom.value) {
    handleError("Veuillez remplir tous les champs obligatoires.");
    return;
  }

  loading.value = true;
  const payload = {
    nom: nom.value,
    prenom: prenom.value,
    id_ref: idRef.value,
    id_proprio: idProprio.value,
  };

  try {
    const response = isEditing.value
      ? await $api.auteur.putAuteur(id.value, authStore.getToken(), payload)
      : await $api.auteur.postAuteur(authStore.getToken(), payload);

    const newId = response.data.id;
    notify(isEditing.value ? "Auteur mis à jour avec succès" : "Auteur créé avec succès", 'success');

    emits('auteurCreated', { ...payload, id: newId });

    // Redirection uniquement si dans une vue
    if (!isModal.value) {
      setTimeout(() => {
        navigation.goToAuteur(newId);
      }, 1500);
    }
  } catch (error) {
    handleError(error, "Erreur lors de l'enregistrement de l'auteur");
  } finally {
    loading.value = false;
  }
};
</script>

<template lang="pug">
div.container.mt-4
  div.position-relative.mb-4
    button.btn.btn-secondary.position-absolute.start-0(
      v-if="isEditing && !isModal",
      @click="navigation.goToAuteur(id)"
    )
      font-awesome-icon(icon="arrow-left")
      span.px-1 Retour à la fiche auteur

    h2.text-center {{ isEditing ? 'Mise à jour de l’auteur' : 'Créer un nouvel auteur' }}

  form(@submit.prevent="submit")
    .row.mb-3
      .col
        label.form-label Nom *
        input.form-control(v-model="nom" required)
      .col
        label.form-label Prénom *
        input.form-control(v-model="prenom" required)

    .row.mb-3
      .col
        label.form-label ID Référence (ID ABES)
        input.form-control(v-model="idRef")
      .col
        label.form-label ID Propriétaire
        input.form-control(v-model="idProprio" disabled)

    .my-4.text-end
      button.btn.btn-primary(type="submit" :disabled="loading")
        span(v-if="loading") Traitement...
        span(v-else) {{ isEditing ? 'Mettre à jour' : 'Valider' }}
</template>

<style scoped>
form {
  max-width: 800px;
  margin: 0 auto;
}
</style>