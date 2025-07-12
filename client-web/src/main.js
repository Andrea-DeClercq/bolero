// Import from external lib
import './assets/main.css'
import { createApp } from 'vue'
import 'bootstrap'
import Pagination from 'v-pagination-3';
import { library } from '@fortawesome/fontawesome-svg-core';
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome';
import { far } from '@fortawesome/free-regular-svg-icons';
import { fas } from '@fortawesome/free-solid-svg-icons';
import { Collapse } from 'vue-collapsed';

// Import from local code
import App from '@/App.vue'
import router from '@/router/router'
import BoleroApi from '@/api/http'
import authStore from '@/stores/authStore'
import { useNavigation } from '@/composables/useNavigation';
import { useErrorHandler } from '@/composables/useErrorHandler';
import { useNotification } from '@/composables/useNotification'

library.add(far, fas);

const app = createApp(App)

const errorHandler = useErrorHandler()
const notification = useNotification(errorHandler)

authStore.checkAuth();

app.use(router)
app.use(BoleroApi)

app.provide('authStore', authStore)
app.provide('navigation', useNavigation(router));
app.provide('errorHandler', errorHandler)
app.provide('notification', notification)

app.component('pagination', Pagination)
app.component('font-awesome-icon', FontAwesomeIcon)
app.component('collapse', Collapse)

app.mount('#app')
