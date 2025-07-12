<script setup>
import { RouterLink, RouterView } from 'vue-router';
import { inject, ref } from 'vue';

const authStore = inject('authStore');
const { error, hasError, resetError } = inject('errorHandler');
const { message, type, visible, clear } = inject('notification');

const menuOpen = ref(false);

function toggleMenu() {
  menuOpen.value = !menuOpen.value;
}

function logout() {
  authStore.logout();
  menuOpen.value = false;
}
</script>

<template lang="pug">
header.navbar
  .navbar-brand
    img.logo(alt="Vue logo" src="@/assets/logo.svg" width="50" height="50")
    span.title(title="Base Ouverte de Liaison Entre Recensions et Ouvrages") Boléro

  button.burger-button.d-md-none(@click="toggleMenu")
    font-awesome-icon(:icon="menuOpen ? 'times' : 'bars'" size="lg")

  nav.navbar-links(:class="{ open: menuOpen }")
    RouterLink.nav-link(to="/" exact-active-class="router-link-active" @click="menuOpen = false") Home
    RouterLink.nav-link(to="/auteurs" exact-active-class="router-link-active" @click="menuOpen = false") Auteurs
    RouterLink.nav-link(to="/ouvrages" exact-active-class="router-link-active" @click="menuOpen = false") Ouvrages
    RouterLink.nav-link(to="/recensions" exact-active-class="router-link-active" @click="menuOpen = false") Recensions

    button.btn.btn-light.ms-md-3.mt-2.mt-md-0(
      v-if="authStore.isAuthenticated"
      @click="logout"
    ) Déconnexion

    RouterLink.btn.btn-primary.ms-md-3.mt-2.mt-md-0(
      v-else
      to="/login"
      @click="menuOpen = false"
    ) Connexion

main.main-content
  transition(name="toast")
    div.toast-notification(v-if="hasError || visible")
      div.toast-header(:class="hasError ? 'toast-error' : 'toast-' + type")
        span {{ hasError ? 'Erreur' : 'Notification' }}
        button.btn-close(@click="hasError ? resetError() : clear()" aria-label="Fermer")
          font-awesome-icon(icon="square-xmark")
      div.toast-body
        span(v-if="hasError") {{ error }}
        span(v-else) {{ message }}

  RouterView(:key="$route.fullPath")
</template>

<style lang="scss">
$primary: #4F7878;
$primary-dark: #364D4D;
$secondary: #D2EDEB;

@import '../node_modules/bootstrap/scss/bootstrap.scss';

body {
  margin: 0;
  font-family: Avenir, Helvetica, Arial, sans-serif;
  overflow-x: hidden;
  box-sizing: border-box;
}

#app {
  display: flex;
  flex-direction: column;
  height: 100vh;
  width: 100%;
}

.navbar {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  background-color: $primary;
  color: white;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 2rem;
  z-index: 1000;
  box-shadow: 0px 2px 4px rgba(0, 0, 0, 0.1);

  .logo {
    height: 60px;
    width: auto;
  }
}
.navbar-brand {
  display: flex;
  align-items: center;

  .title {
    margin-left: 0.75rem;
    font-size: 1.5rem;
    font-weight: bold;
    color: white;
    cursor: help; // pour l’info-bulle au survol
    white-space: nowrap;
  }
}
.burger-button {
  background: transparent;
  border: none;
  color: white;
  font-size: 1.5rem;
  cursor: pointer;
  display: none;

  @media (max-width: 767px) {
    display: block;
  }
}

.navbar-links {
  display: flex;
  align-items: center;
  gap: 1rem;

  .nav-link {
    text-decoration: none;
    color: white;
    font-weight: bold;
    padding: 0.5rem 1rem;
    border-radius: 5px;
    transition: background-color 0.3s ease;

    &:hover {
      background-color: $secondary;
      color: $primary-dark;
    }

    &.router-link-active {
      background-color: $primary-dark;
      color: white;
    }
  }

  @media (max-width: 767px) {
    display: none;
    position: absolute;
    top: 70px;
    left: 0;
    width: 100%;
    flex-direction: column;
    align-items: flex-start;
    padding: 1rem 2rem;
    background-color: $primary;

    &.open {
      display: flex;
    }

    .nav-link,
    .btn {
      width: 100%;
      text-align: left;
    }
  }
}

.main-content {
  margin-top: 70px;
  padding: 2rem;
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
  width: 100%;
  box-sizing: border-box;
}

.toast-notification {
  position: fixed;
  bottom: 20px;
  right: 20px;
  max-width: 350px;
  border-radius: 8px;
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);
  overflow: hidden;
  z-index: 2000;
  display: flex;
  flex-direction: column;
  font-family: inherit;

  .toast-header {
    padding: 0.5rem 1rem;
    color: #fff;
    font-weight: bold;
    display: flex;
    justify-content: space-between;
    align-items: center;

    &.toast-error {
      background-color: #dc3545;
    }

    &.toast-success {
      background-color: #4F7878;
    }

    &.toast-info {
      background-color: #0d6efd;
    }

    .btn-close {
      background: transparent;
      border: none;
      font-size: 1.2rem;
      line-height: 1;
      color: #000000;
      cursor: pointer;
    }
  }

  .toast-body {
    background-color: #f8f9fa;
    padding: 1rem;
    color: #212529;
  }
}

.toast-enter-active,
.toast-leave-active {
  transition: opacity 0.4s ease, transform 0.4s ease;
}
.toast-enter-from,
.toast-leave-to {
  opacity: 0;
  transform: translateY(20px);
}
</style>