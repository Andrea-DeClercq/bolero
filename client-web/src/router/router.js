import { createRouter, createWebHistory } from 'vue-router'
import { authStore } from '@/stores/authStore';

import Auteur from '@/views/Auteurs/Auteur.vue'
import AuteurForm from '@/views/Auteurs/AuteurForm.vue';
import AuteursList from '@/views/Auteurs/AuteursList.vue'
import HomeView from '../views/HomeView.vue'
import Login from '@/views/Login.vue'
import Ouvrage from '@/views/Ouvrages/Ouvrage.vue'
import OuvrageForm from '@/views/Ouvrages/OuvrageForm.vue'
import OuvragesList from '@/views/Ouvrages/OuvragesList.vue'
import Recension from '@/views/Recensions/Recension.vue'
import RecensionForm from '@/views/Recensions/RecensionForm.vue';
import RecensionsList from '@/views/Recensions/RecensionsList.vue'

const routes = [
  {
    path: "/",
    name: "home",
    component: HomeView,
    meta: {
      title: "Home",
    },
  },
  /*************************************************************************************************
   *    AUTEURS
   *************************************************************************************************/
  {
    path: "/auteurs",
    children: [
      {
        path: "",
        name: "auteurs-list",
        component: AuteursList,
        meta: {
          title: "Liste des auteurs",
        },
      },
      {
        path: ":id",
        name: "auteur",
        component: Auteur,
        meta: {
          title: "Fiche auteur",
        },
      },
      {
        path: ":id/edit",
        name: "auteur-edit",
        component: AuteurForm,
        meta: {
          title: "Edition de l'auteur",
          requiresAuth: true,
        }
      },
      {
        path: "new",
        name: "auteur-new",
        component: AuteurForm,
        meta: {
          title: "Nouvel Auteur",
          requiresAuth: true,
        }
      }
    ]
  },
  /*************************************************************************************************
   *    OUVRAGES
   *************************************************************************************************/
  {
    path: "/ouvrages",
    children: [
      {
        path: "",
        name: "ouvrages-list",
        component: OuvragesList,
        meta: {
          title: "Liste des ouvrages",
        },
      },
      {
        path: ":id",
        name: "ouvrage",
        component: Ouvrage,
        meta: {
          title: "Fiche ouvrage"
        },
      },
      {
        path: ":id/edit",
        name: "ouvrage-edit",
        component: OuvrageForm,
        meta: {
          title: "Edition de l'ouvrage",
          requiresAuth: true 
        },
      },
      {
        path: "new",
        name: "ouvrage-new",
        component: OuvrageForm,
        meta: {
          title: "Ajout d'un ouvrage",
          requiresAuth: true 
        },
      }
    ]
  },
  /*************************************************************************************************
   *    RECENSIONS
   *************************************************************************************************/
  {
    path: "/recensions",
    children: [
      {
        path: "",
        name: "recensions-list",
        component: RecensionsList,
        meta: {
          title: "Liste des recensions"
        },
      },
      {
        path: ":id",
        name: "recension",
        component: Recension,
        meta: {
          title: "Fiche recension"
        }
      },
      {
        path: ":id/edit",
        name: "recension-edit",
        component: RecensionForm,
        meta: {
          title: "Edition de la recension",
          requiresAuth: true,
        }
      },
      {
        path: "new",
        name: "recension-new",
        component: RecensionForm,
        meta: {
          title: "Nouvelle recension",
          requiresAuth: true,
        }
      }
    ]
  },
  /*************************************************************************************************
   *    LOGIN
   *************************************************************************************************/
  {
    path: "/login",
    name: "login",
    component: Login,
    meta: {
      title: "Connexion"
    }
  },
];


const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: routes
})

router.beforeEach((to, from, next) => {
  document.title = `${to.meta.title}`
  if (to.matched.some(record => record.meta.requiresAuth) && !authStore.isAuthenticated) {
    next("/login");
  } else {
    next();
  }
});

export default router
