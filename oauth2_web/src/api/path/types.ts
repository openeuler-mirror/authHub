// Copyright (c) Huawei Technologies Co., Ltd. 2023-2024. All rights reserved.
// licensed under the Mulan PSL v2.
// You can use this software according to the terms and conditions of the Mulan PSL v2.
// You may obtain a copy of Mulan PSL v2 at:
//      http://license.coscl.org.cn/MulanPSL2
// THIS SOFTWARE IS PROVIDED ON AN 'AS IS' BASIS, WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR
// IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT, MERCHANTABILITY OR FIT FOR A PARTICULAR
// PURPOSE.
// See the Mulan PSL v2 for more details.

export type TokenEndpoinAuthMethod =
  | "client_secret_post"
  | "client_secret_basic"
  | "none";
export type AllowedResponsesTypes = "code" | "token";
export type AllowedGrantTypes = "authorization_code" | "client_credentials";
export type AllowedScopeTypes =
  | "openid"
  | "username"
  | "email"
  | "phone"
  | "offline_access";

export interface ClientInfo {
  client_id: string;
  client_id_issued_at: number;
  client_secret: string;
  client_secret_expires_at: number;
}

export interface ClientMetadata {
  client_name: string;
  client_uri: string;
  grant_types: AllowedGrantTypes[];
  logout_callback_uris: string[];
  redirect_uris: string[];
  register_callback_uris: string[];
  response_types: AllowedResponsesTypes[];
  scope: AllowedScopeTypes[];
  skip_authorization: boolean;
  token_endpoint_auth_method: TokenEndpoinAuthMethod;
}

export interface Application {
  client_info: ClientInfo;
  client_metadata: ClientMetadata;
}

export interface ApplicationReqParams {
  client_name?: string;
  client_uri: string;
  redirect_uris: string[];
  skip_authorization: boolean;
  register_callback_uris?: string[];
  logout_callback_uris?: string[];
  scope?: AllowedScopeTypes[];
  grant_types: AllowedGrantTypes[];
  response_types: AllowedResponsesTypes[];
  token_endpoint_auth_method: TokenEndpoinAuthMethod;
}
