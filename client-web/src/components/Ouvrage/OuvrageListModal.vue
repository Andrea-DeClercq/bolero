<script setup>
import { inject, ref, defineEmits, defineProps, onMounted, watch } from "vue";
import { useSearchFields } from "@/composables/useSearchFields";
import { normalizeOuvrage } from "@/constants/utils";

const $api = inject("$api");

const emits = defineEmits(["update:selectedBooks"]);
const props = defineProps({
  selectedBooks: {
    type: Array,
    default: () => [],
  },
});

const selectedBooks = ref([]);

watch(
  () => props.selectedBooks,
  (newVal) => {
    selectedBooks.value = [...newVal];
  },
  { immediate: true, deep: true }
);

const availableFields = [
  { key: "id", label: "ID" },
  { key: "sous_titre", label: "Sous-titre" },
  { key: "volume", label: "Volume" },
  { key: "ean", label: "EAN" },
  { key: "portail", label: "Portail" },
  { key: "auteur_nom", label: "Nom de l'auteur" },
  { key: "auteur_prenom", label: "Prénom de l'auteur" },
  { key: "id_auteur", label: "ID Auteur" },
  { key: "id_proprio", label: "ID Propriétaire" },
  { key: "traducteur", label: "Traducteur" },
  { key: "langue", label: "Langue" },
];

const fixedFields = {
  titre: "",
  editeur: "",
  anneeParution: ""
};

const {
  searchFields,
  fixedValues,
  addField,
  removeField,
  removeAllFields,
  filteredAvailableFields,
  updateAvailableFields
} = useSearchFields(availableFields, fixedFields);

const ouvrages = ref([]);
const currentPage = ref(1);
const limit = ref(20);
const totalItems = ref(0);

const searchOuvrages = async (page) => {
  currentPage.value = page;
  const params = {
    page: currentPage.value,
    limit: limit.value
  };

  if (fixedValues.titre) params.titre = fixedValues.titre;
  if (fixedValues.editeur) params.editeur = fixedValues.editeur;
  if (fixedValues.anneeParution) params["annee_parution"] = fixedValues.anneeParution;

  searchFields.value.forEach((field) => {
    if (field.key && field.value) {
      params[field.key] = field.value;
    }
  });

  try {
    const response = await $api.ouvrage.getOuvrages(params);
    ouvrages.value = response.data.ouvrages || [];
    totalItems.value = response.data.total || 0;
  } catch (err) {
    console.error("Erreur lors du chargement des ouvrages :", err);
  }
};

const toggleOuvrage = (ouvrage) => {
  const index = selectedBooks.value.findIndex((o) => o.id === ouvrage.id);

  const normalizedOuvrage = normalizeOuvrage(ouvrage)

  if (index === -1) {
    selectedBooks.value.push(normalizedOuvrage);
  } else {
    selectedBooks.value.splice(index, 1);
  }

  emits("update:selectedBooks", [...selectedBooks.value]);
};

const isSelected = (ouvrage) => selectedBooks.value.some((o) => o.id === ouvrage.id);

onMounted(() => {
  searchOuvrages(1);
});
</script>

<template lang="pug">
  div
    h5.text-center.mb-3 Sélectionner un ouvrage

    form(@submit.prevent="searchOuvrages(1)").pb-3
      .row.mb-2
        .col
          input.form-control(type="text" placeholder="Titre" v-model="fixedValues.titre")
        .col
          input.form-control(type="text" placeholder="Éditeur" v-model="fixedValues.editeur")
        .col
          input.form-control(type="text" placeholder="Année" v-model="fixedValues.anneeParution")
        .col-auto.d-flex.align-items-end
          button.btn.btn-primary(type="submit") Rechercher

      .row.mb-2(v-for="(field, index) in searchFields" :key="index")
        .col.d-flex.align-items-end
          select.form-select(v-model="field.key" @change="updateAvailableFields")
            option(value="" disabled) -- Champ --
            option(v-for="option in filteredAvailableFields(index)" :value="option.key") {{ option.label }}
        .col.d-flex.align-items-end
          input.form-control(v-model="field.value" :placeholder="field.key || 'Valeur'" :disabled="!field.key")
        .col-auto.d-flex.align-items-center
          button.btn.btn-outline-danger(@click="removeField(index)") ✕
      .row.mb-3
        .col
          button.btn.btn-secondary(type="button" @click="addField") Ajouter un champ
          button.btn.btn-light.ms-2(type="button" @click="removeAllFields") Tout supprimer

    div(v-if="ouvrages.length > 0")
      ul.list-group
        li.list-group-item(
          v-for="ouvrage in ouvrages"
          :key="ouvrage.id"
          :class="{ 'active': isSelected(ouvrage) }"
          @click="toggleOuvrage(ouvrage)"
          role="button"
        )
          div.row
            span(v-html="ouvrage.titre") 
            div(v-if="ouvrage['sous_titre']") — 
              span(v-html="ouvrage['sous_titre']")
            span {{ ouvrage.editeur }} ({{ ouvrage.annee_parution }})
          font-awesome-icon.ms-2(
            v-if="isSelected(ouvrage)"
            icon="check-circle"
            class="text-secondary"
          )
      div.d-flex.justify-content-center.mt-3
        pagination(
          :options="{ hideCount: true }"
          v-model="currentPage"
          :records="totalItems"
          :per-page="limit"
          @paginate="searchOuvrages"
        )
    div(v-else)
      p.text-muted Aucun ouvrage trouvé.
</template>

<style scoped>
.list-group-item.active {
  background-color: #436666 !important;
  color: white;
  font-weight: bold;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>