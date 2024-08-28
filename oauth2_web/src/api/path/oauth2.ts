// Copyright (c) Huawei Technologies Co., Ltd. 2023-2024. All rights reserved.
// licensed under the Mulan PSL v2.
// You can use this software according to the terms and conditions of the Mulan PSL v2.
// You may obtain a copy of Mulan PSL v2 at:
//      http://license.coscl.org.cn/MulanPSL2
// THIS SOFTWARE IS PROVIDED ON AN 'AS IS' BASIS, WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR
// IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT, MERCHANTABILITY OR FIT FOR A PARTICULAR
// PURPOSE.
// See the Mulan PSL v2 for more details.
import { http } from '@/api/request'
import { Application, ApplicationReqParams } from './types'

/**
 * Retrieves a list of all OAuth2 applications.
 *
 * @return {Object} An object containing an array of Application objects and the total number of applications.
 */
function queryAllApplications(): Promise<[any, { applications: Application[], number: number } | undefined]> {
  return http.get<{
    applications: Application[]
    number: number
  }>('/oauth2/applications')
}

/**
 * Creates a new OAuth2 application.
 *
 * @param {Object} params - Application creation parameters.
 * @param {string} params.client_name - The name of the client.
 * @param {string} params.client_uri - The URI of the client.
 * @param {string[]} params.redirect_uris - The redirect URIs of the client.
 * @param {boolean} params.skip_authorization - Whether to skip authorization.
 * @param {string[]} [params.register_callback_uris] - The register callback URIs of the client.
 * @param {string[]} [params.logout_callback_uris] - The logout callback URIs of the client.
 * @param {string[]} [params.scope] - The scope of the client.
 * @param {AllowedGrantTypes[]} params.grant_types - The grant types of the client.
 * @param {AllowedResponsesTypes[]} params.response_types - The response types of the client.
 * @param {TokenEndpoinAuthMethod} params.token_endpoint_auth_method - The token endpoint authentication method of the client.
 * @return {Promise} A promise that resolves with the result of the application creation request.
 */
function createApplication(params: ApplicationReqParams): Promise<[any, unknown]> {
  return http.post('/oauth2/applications/register', params)
}

/**
 * Deletes an OAuth2 application by its client ID.
 *
 * @param {string} client_id - The client ID of the application to delete.
 * @return {Promise} A promise that resolves with the result of the deletion request.
 */
function deleteApplication(client_id: string): Promise<[any, unknown]> {
  return http.delete(`/oauth2/applications/${client_id}`)
}

/**
 * Retrieves an OAuth2 application by its client ID.
 *
 * @param {string} client_id - The client ID of the application to retrieve.
 * @return {Promise<[any, Application | undefined]>} A promise that resolves with the result of the retrieval request.
 */
function queryApplicationByClientId(client_id: string): Promise<[any, Application | undefined]> {
  return http.get<Application>(`/oauth2/applications/${client_id}`)
}

/**
 * Updates an existing OAuth2 application.
 *
 * @param {string} clientId - The client ID of the application to update.
 * @param {Object} params - The updated application parameters.
 * @param {string} params.client_name - The name of the client.
 * @param {string} params.client_uri - The URI of the client.
 * @param {string[]} params.redirect_uris - The redirect URIs of the client.
 * @param {boolean} params.skip_authorization - Whether to skip authorization.
 * @param {string[]} [params.register_callback_uris] - The register callback URIs of the client.
 * @param {string[]} [params.logout_callback_uris] - The logout callback URIs of the client.
 * @param {string[]} [params.scope] - The scope of the client.
 * @param {AllowedGrantTypes[]} params.grant_types - The grant types of the client.
 * @param {AllowedResponsesTypes[]} params.response_types - The response types of the client.
 * @param {TokenEndpoinAuthMethod} params.token_endpoint_auth_method - The token endpoint authentication method of the client.
 * @return {Promise<[any, unknown]>} A promise that resolves with the result of the update request.
 */
function updateApplication(clientId: string, params: ApplicationReqParams): Promise<[any, unknown]> {
  return http.put(`/oauth2/applications/${clientId}`, params)
}



export const oauth2Api = {
  queryAllApplications,
  createApplication,
  deleteApplication,
  queryApplicationByClientId,
  updateApplication,
}
