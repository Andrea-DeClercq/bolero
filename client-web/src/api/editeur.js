import { configureRequestForm } from "@/api/config";

export default ($http) => ({
    async getEditeurs(params) {
        const response = await $http.get("bolero/editeurs", { params });
        return response;
    },

    async postEditeur(token, params) {
        const { config, formData } = configureRequestForm(token, params);
        const response = await $http.post("bolero/editeurs", formData, config);
        return response;
    },
});
