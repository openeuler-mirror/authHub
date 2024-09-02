#!/usr/bin/python3
# ******************************************************************************
# Copyright (c) Huawei Technologies Co., Ltd. 2021-2024. All rights reserved.
# licensed under the Mulan PSL v2.
# You can use this software according to the terms and conditions of the Mulan PSL v2.
# You may obtain a copy of Mulan PSL v2 at:
#     http://license.coscl.org.cn/MulanPSL2
# THIS SOFTWARE IS PROVIDED ON AN 'AS IS' BASIS, WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT, MERCHANTABILITY OR FIT FOR A PARTICULAR
# PURPOSE.
# See the Mulan PSL v2 for more details.
# ******************************************************************************/
from authlib.integrations.flask_oauth2 import AuthorizationServer as AuthlibAuthorizationServer
from authlib.oauth2.rfc6749 import OAuth2Request as _OAuth2Request
from authlib.oauth2.rfc6749.errors import InsecureTransportError, InvalidScopeError
from authlib.oauth2.rfc6749.util import scope_to_list
from flask import request as flask_req
from flask.wrappers import Request
from sqlalchemy.exc import SQLAlchemyError

from oauth2_provider.app.core.token import jwt_token
from oauth2_provider.database.table import OAuth2ClientScopes


class OAuth2Request(_OAuth2Request):
    def __init__(self, request: Request):
        InsecureTransportError.check(request.url)
        #: HTTP method
        self.method = request.method
        self.uri = request.url
        self.body = None
        #: HTTP headers
        self.headers = request.headers or {}

        self.client = None
        self.auth_method = None
        self.user = None
        self.authorization_code = None
        self.refresh_token = None
        self.credential = None
        self._request = request

    @property
    def args(self):
        return self._request.args

    @property
    def form(self):
        return self._request.form or self._request.json

    @property
    def data(self):
        return self._request.values or self._request.json


class AuthorizationServer(AuthlibAuthorizationServer):

    def validate_requested_scope(self, scope, state=None, request: OAuth2Request = None):
        """Validate if requested scope is supported by Authorization Server.
        Developers CAN re-write this method to meet your needs.
        """
        if not scope:
            return

        try:
            if request.client.skip_authorization:
                self.scopes_supported = scope_to_list(request.client.scope)
            else:
                oauth2_client_scopes = OAuth2ClientScopes.query.filter_by(
                    username=request.user, client_id=request.client_id
                ).one_or_none()

                if oauth2_client_scopes:
                    self.scopes_supported = scope_to_list(oauth2_client_scopes.scope)
                else:
                    self.scopes_supported = scope_to_list(request.client.scope)
        except SQLAlchemyError:
            raise InvalidScopeError(state=state)

        scopes = set(scope_to_list(scope))
        if not set(self.scopes_supported).issuperset(scopes):
            raise InvalidScopeError(state=state)

    def create_oauth2_request(self, request):
        return OAuth2Request(flask_req)

    def create_bearer_token_generator(self, config):
        """Create a generator function for generating ``token`` value. This
        method will create a Bearer Token generator with
        :class:`authlib.oauth2.rfc6750.BearerToken`.

        Configurable settings:

        1. OAUTH2_ACCESS_TOKEN_GENERATOR: Boolean or import string, default is True.
        2. OAUTH2_REFRESH_TOKEN_GENERATOR: Boolean or import string, default is False.
        3. OAUTH2_TOKEN_EXPIRES_IN: Dict or import string, default is None.

        By default, it will not generate ``refresh_token``, which can be turn on by
        configure ``OAUTH2_REFRESH_TOKEN_GENERATOR``.

        Here are some examples of the token generator::

            OAUTH2_ACCESS_TOKEN_GENERATOR = 'your_project.generators.gen_token'

            # and in module `your_project.generators`, you can define:

            def gen_token(client, grant_type, user, scope):
                # generate token according to these parameters
                token = create_random_token()
                return f'{client.id}-{user.id}-{token}'

        Here is an example of ``OAUTH2_TOKEN_EXPIRES_IN``::

            OAUTH2_TOKEN_EXPIRES_IN = {
                'authorization_code': 864000,
                'urn:ietf:params:oauth:grant-type:jwt-bearer': 3600,
            }
        """
        return jwt_token
