import { configureRequestForm, configureAuthRequest } from "@/api/config";

export default ($http) => ({
    async getAuteurs(params) {
        const response = await $http.get('bolero/auteurs', {params});
        return response;
    },
    async getAuteurDetails(id){ 
        const response = await $http.get(`bolero/auteurs/${id}`);
        return response
    },
    async postAuteur(token, params) {
        const { config, formData } = configureRequestForm(token, params);

        const response = await $http.post(
            'bolero/auteurs',
            formData,
            config
        );
        return response;
    },
    async putAuteur(id, token, params) {
        const { config, formData } = configureRequestForm(token, params);

        const response = await $http.put(
            `bolero/auteurs/${id}`,
            formData,
            config
        );
        return response;
    },
    async deleteAuteur(id, token) {
        const headers = configureAuthRequest(token);
        return await $http.delete(`bolero/auteurs/${id}`, headers)
    },
    async exportAuteurs(params) {
        const response = await $http.get("bolero/auteurs/export", {
          params,
          responseType: "blob",
        });
        return response.data;
    },
});