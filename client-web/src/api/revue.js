import { configureRequestForm } from "@/api/config";

export default ($http) => ({
    async getRevues(params) {
        const response = await $http.get("bolero/revues", { params });
        return response;
    },

    async postRevue(token, params) {
        const { config, formData } = configureRequestForm(token, params);
        const response = await $http.post("bolero/revues", formData, config);
        return response;
    },
});