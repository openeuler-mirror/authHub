#!/usr/bin/python3
# ******************************************************************************
# Copyright (c) Huawei Technologies Co., Ltd. 2021-2022. All rights reserved.
# licensed under the Mulan PSL v2.
# You can use this software according to the terms and conditions of the Mulan PSL v2.
# You may obtain a copy of Mulan PSL v2 at:
#     http://license.coscl.org.cn/MulanPSL2
# THIS SOFTWARE IS PROVIDED ON AN 'AS IS' BASIS, WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT, MERCHANTABILITY OR FIT FOR A PARTICULAR
# PURPOSE.
# See the Mulan PSL v2 for more details.
# ******************************************************************************/
from authlib.oauth2.rfc6750.errors import InsufficientScopeError, InvalidTokenError
from authlib.oauth2.rfc7523.validator import JWTBearerTokenValidator as _JWTBearerTokenValidator
from vulcanus.log.log import LOGGER

from oauth2_provider.app.core.server import OAuth2Request
from oauth2_provider.database.table import OAuth2Token
from oauth2_provider.manage import db


class JWTBearerTokenValidator(_JWTBearerTokenValidator):
    """
    validator jwt bearer token
    """

    token_cls = OAuth2Token

    def __init__(self, public_key=None, issuer=None, realm=None, **extra_attributes):
        super().__init__(public_key, issuer, realm, **extra_attributes)

    def authenticate_token(self, token_string):
        """
        A method to query token from database with the given token string.
        Developers MUST re-implement this method.

        :param token_string: A string to represent the access_token.
        :return: token
        """

        try:
            token = db.session.query(OAuth2Token).filter_by(access_token=token_string).first()
            if not token:
                LOGGER.warning("Token not found: %s", token_string)

        except Exception as e:
            LOGGER.error("Failed to query token: %s", e)
            token = None
        return token

    def validate_token(self, token, scopes, request: OAuth2Request):
        """Check if token is active and matches the requested scopes."""

        if not token:
            raise InvalidTokenError(realm=self.realm, extra_attributes=self.extra_attributes)

        if token.is_revoked():
            raise InvalidTokenError("The token has been revoked")

        # Check that the token is by the client
        if token.client_id != request.client_id:
            raise InvalidTokenError("The token does not match the client")

        if self.scope_insufficient(token.get_scope(), scopes):
            raise InsufficientScopeError()

    def validate_request(self, request):
        pass
