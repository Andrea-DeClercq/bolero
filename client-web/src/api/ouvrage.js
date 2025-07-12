import { configureRequestForm, configureAuthRequest } from "@/api/config";

export default ($http) => ({
    async getOuvrages(params) {
        const response = await $http.get(`bolero/ouvrages`, { params });
        return response;
    },
    async getOuvrageDetails(id) {
        const response = await $http.get(`bolero/ouvrages/${id}`);
        return response;
    },
    async postOuvrage(token, params) {
        const { config, formData } = configureRequestForm(token, params);

        const response = await $http.post(
            `bolero/ouvrages`,
            formData,
            config
        );
        return response;
    },
    async putOuvrage(id, token, params) {
        const { config, formData } = configureRequestForm(token, params);

        const response = await $http.put(
            `bolero/ouvrages/${id}`,
            formData,
            config
        );
        return response;
    },
    async deleteOuvrage(id, token) {
        const headers = configureAuthRequest(token);
        return await $http.delete(`bolero/ouvrages/${id}`, headers)
    },
    async exportOuvrages(params) {
        const response = await $http.get("bolero/ouvrages/export", {
          params,
          responseType: "blob",
        });
        return response.data;
    }
});