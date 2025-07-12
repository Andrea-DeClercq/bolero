<script setup>
import { inject, ref } from 'vue';

const $api = inject('$api')
const authStore = inject('authStore')
const navigation = inject('navigation')
const identifier = ref('');
const password = ref('');
const rememberMe = ref(false);
const errorMessage = ref('');

async function login() {
    try {
        const json = {
            identifier: identifier.value,
            type: "username",
            password: password.value,
            remember_me: rememberMe.value,
        };

        const response = await $api.auth.login(json);
        if (response.data.token) {
            const token = response.data.token;
            const expiration = rememberMe.value
                ? new Date(Date.now() + 7 * 24 * 60 * 60 * 1000)
                : new Date(Date.now() + 1 * 60 * 60 * 1000);

            document.cookie = `authToken=${token}; expires=${expiration.toUTCString()}; path=/; samesite=None; secure`;
            // Mettre à jour l'état de l'authentification
            authStore.checkAuth();
            navigation.goToHome()
        } else {
            errorMessage.value = 'Une erreur est survenue.';
            }
    } catch (error) {
        if (error.response?.status === 401) {
        errorMessage.value = error.response.data.data.description || 'Identifiants invalides.';
        } else {
        console.error('Erreur lors de la connexion :', error);
        errorMessage.value = 'Une erreur est survenue. Veuillez réessayer.';
        }
    }
}
</script>

<template lang="pug">
div.container.mt-5
  h1.text-center.mb-4 Connexion
  form.w-50.mx-auto.needs-validation(novalidate, @submit.prevent="login")
    div.mb-3
      label.form-label(for="identifier") Identifiant
      input#identifier.form-control(type="text", v-model="identifier", required)

    div.mb-3
      label.form-label(for="password") Mot de passe
      input#password.form-control(type="password", v-model="password", required)

    div.form-check.mb-3
      input#remember_me.form-check-input(type="checkbox", v-model="rememberMe")
      label.form-check-label(for="remember_me") Se souvenir de moi

    div.text-center
      button.btn.btn-primary(type="submit") Connexion

  div.text-danger.text-center.mt-3(v-if="errorMessage") {{ errorMessage }}
</template>
