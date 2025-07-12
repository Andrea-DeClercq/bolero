import { configureRequestForm, configureAuthRequest } from "@/api/config";

export default ($http) => ({
  /**********************************************************************
   * POST simple
   *********************************************************************/
  async postRelation(token, params) {
    const { config, formData } = configureRequestForm(token, params);

    const response = await $http.post(
      'bolero/relations',
      formData,
      config
    );
    return response;
  },

  /**********************************************************************
   * POST batch
   *********************************************************************/
  async postRelationsBatch(token, relations) {
    const headers = configureAuthRequest(token);
    const payload = { relations };
    const response = await $http.post(
      'bolero/relations/batch',
      payload,
      headers
    );
    return response;
  },

  /**********************************************************************
   * DELETE simple
   *********************************************************************/
  async deleteAuthorBookRelation(id, token) {
    const headers = configureAuthRequest(token);
    return await $http.delete(`bolero/relations/auteurs-ouvrages/${id}`, headers);
  },
  async deleteAuthorReviewRelation(id, token) {
    const headers = configureAuthRequest(token);
    return await $http.delete(`bolero/relations/auteurs-recensions/${id}`, headers);
  },
  async deleteBookReviewRelation(id, token) {
    const headers = configureAuthRequest(token);
    return await $http.delete(`bolero/relations/ouvrages-recensions/${id}`, headers);
  },

  /**********************************************************************
   * DELETE batch
   *********************************************************************/
  async deleteAuthorBookRelationsBatch(token, ids) {
    const headers = configureAuthRequest(token);
    const payload = { relations: ids.map((id) => ({ id })) };
    return await $http.delete(
      'bolero/relations/auteurs-ouvrages/batch',
      { ...headers, data: payload }
    );
  },

  async deleteAuthorReviewRelationsBatch(token, ids) {
    const headers = configureAuthRequest(token);
    const payload = { relations: ids.map((id) => ({ id })) };
    return await $http.delete(
      'bolero/relations/auteurs-recensions/batch',
      { ...headers, data: payload }
    );
  },

  async deleteBookReviewRelationsBatch(token, ids) {
    const headers = configureAuthRequest(token);
    const payload = { relations: ids.map((id) => ({ id })) };
    return await $http.delete(
      'bolero/relations/ouvrages-recensions/batch',
      { ...headers, data: payload }
    );
  },
});