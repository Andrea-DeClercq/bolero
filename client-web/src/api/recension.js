import { configureRequestForm, configureAuthRequest } from "@/api/config";

export default ($http) => ({
    async getRecensions(params) {
        const response = await $http.get(`bolero/recensions`, {params});
        return response;
    },
    async getRecensionDetails(id) {
        const response = await $http.get(`bolero/recensions/${id}`);
        return response;
    },
    async postRecension(token, params) {
        const { config, formData } = configureRequestForm(token, params);

        const response = await $http.post(
            `bolero/recensions`,
            formData,
            config
        );
        return response;
    },
    async putRecension(id, token, params) {
        const { config, formData } = configureRequestForm(token, params);

        const response = await $http.put(
            `bolero/recensions/${id}`,
            formData,
            config
        );
        return response; 
    },
    async deleteRecension(id, token) {
        const headers = configureAuthRequest(token);
        return await $http.delete(`bolero/recensions/${id}`, headers)
    },
    async exportRecensions(params) {
        const response = await $http.get("bolero/recensions/export", {
          params,
          responseType: "blob",
        });
        return response.data;
    },
});