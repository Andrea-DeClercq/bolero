// Imports from external lib
import axios from 'axios';

// Import from local code
import setupAuteur from '@/api/auteur';
import setupEditeur from '@/api/editeur';
import setupLogin from '@/api/login';
import setupOuvrage from '@/api/ouvrage';
import setupRecension from '@/api/recension';
import setupRelation from '@/api/relation';
import setupRevue from '@/api/revue';

// Création de l'instance HTTP avec Axios
const $http = axios.create({
  timeout: 30000,
  withCredentials: false,
  baseURL: import.meta.env.VITE_API_URL,
});


// Configuration des modules API
const $api = {
  auteur: setupAuteur($http),
  auth: setupLogin($http),
  editeur: setupEditeur($http),
  ouvrage: setupOuvrage($http),
  recension: setupRecension($http),
  relation: setupRelation($http),
  revue: setupRevue($http),
};

// Export de l'instance HTTP et des modules API pour injection
export default {
  install(app) {
    // Utilisation de provide pour partager $http et $api
    app.provide('$http', $http);
    app.provide('$api', $api);
  },
};

// Export pour un usage direct si nécessaire
export { $http, $api };