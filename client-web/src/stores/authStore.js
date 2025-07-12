import { reactive } from 'vue';
import { jwtDecode } from 'jwt-decode';

export const authStore = reactive({
  isAuthenticated: false,
  checkAuth() {
    const token = this.getCookie('authToken');
    this.isAuthenticated = !!token;
  },  
  logout() {
    document.cookie = 'authToken=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/; samesite=None; secure';
    this.isAuthenticated = false;
  },
  getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
    return null;
  },
  getToken() {
    const token = this.getCookie('authToken');
    return token;
  },
  getDecodedToken() {
    const token = document.cookie.split("; ").find(row => row.startsWith("authToken="))?.split("=")[1] || null;
    return token ? jwtDecode(token) : null;
  },
  // Permet de récupérer l'id_portail de l'utilisateur pour l'autocomplétion des formulaires.
  getUserPortailId() {
    return this.getDecodedToken()?.sub.id_portail || null;
  },
});

export default authStore;
