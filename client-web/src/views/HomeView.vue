<script setup>
import { inject } from 'vue';

const navigation = inject('navigation');
</script>

<template lang="pug">
main.container.mt-5
  .row
    .col-12.col-md-6.mb-4.d-flex.flex-column.align-items-center
      h2.mb-4.text-primary.text-center Ouvrages
      button.btn.btn-outline-primary.mb-3.w-100.w-md-75(@click="navigation.goToSearchOuvrage()")
        font-awesome-icon(icon="magnifying-glass" class="me-2")
        | Rechercher un ouvrage
      button.btn.btn-success.w-100.w-md-75(@click="navigation.goToAddOuvrage()")
        font-awesome-icon(icon="book" class="me-2")
        | Ajouter un ouvrage

    .col-12.col-md-6.mb-4.d-flex.flex-column.align-items-center
      h2.mb-4.text-primary.text-center Recensions
      button.btn.btn-outline-primary.mb-3.w-100.w-md-75(@click="navigation.goToSearchRecension()")
        font-awesome-icon(icon="magnifying-glass" class="me-2")
        | Rechercher une recension
      button.btn.btn-success.w-100.w-md-75(@click="navigation.goToAddRecension()")
        font-awesome-icon(icon="pen-to-square" class="me-2")
        | Ajouter une recension
</template>

<style scoped>
@media (max-width: 767px) {
  h2 {
    font-size: 1.5rem;
  }

  button {
    font-size: 1rem;
  }
}
</style>