export default ($http) => ({
    async login(data) {
        const response = await $http.post('auth/login', data);
        return response.data;
    }
});