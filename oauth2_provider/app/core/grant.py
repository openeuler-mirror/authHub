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
from copy import deepcopy

from authlib.oauth2.rfc6749 import grants
from authlib.oauth2.rfc6749.errors import OAuth2Error
from authlib.oidc.core.grants import OpenIDCode as _OpenIDCode
from authlib.oidc.core.grants import OpenIDHybridGrant as _OpenIDHybridGrant
from authlib.oidc.core.grants import OpenIDImplicitGrant as _OpenIDImplicitGrant
from sqlalchemy.exc import SQLAlchemyError
from vulcanus.log.log import LOGGER

from oauth2_provider.database.table import OAuth2AuthorizationCode, OAuth2Token, User
from oauth2_provider.manage import db

JWT_CONFIG = {
    'key': None,
    'alg': 'HS256',
    'exp': 604800,
    'iss': "oauthhub",
    'aud': None,
}


class AuthorizationCodeGrant(grants.AuthorizationCodeGrant):
    """
    Authorization code grant type.
    """

    TOKEN_ENDPOINT_AUTH_METHODS = [
        'client_secret_basic',
        'client_secret_post',
        'none',
    ]

    def validate_requested_scope(self):
        """Validate if requested scope is supported by Authorization Server."""
        scope = self.request.scope
        state = self.request.state
        return self.server.validate_requested_scope(scope, state, self.request)

    def save_authorization_code(self, code, request):
        """
        Save authorization code to database

        :param code: Authorization code
        :param request: OAuth2Request

        :return: authorization code object or raise OAuth2Error
        """

        try:
            if OAuth2AuthorizationCode.query.filter_by(code=code, client_id=request.client.client_id).one_or_none():
                raise OAuth2Error('invalid_code')

            code_challenge = request.data.get('code_challenge')
            code_challenge_method = request.data.get('code_challenge_method')
            auth_code = OAuth2AuthorizationCode(
                code=code,
                client_id=request.client.client_id,
                redirect_uri=request.redirect_uri,
                scope=request.scope,
                username=request.user,
                code_challenge=code_challenge,
                code_challenge_method=code_challenge_method,
            )

            db.session.add(auth_code)
            db.session.commit()
        except SQLAlchemyError as error:
            LOGGER.error('Failed to save authorization code: %s', error)
            raise OAuth2Error("Failed to save authorization code")

        return auth_code

    def query_authorization_code(self, code, client):
        """
        Query an authorization code.

        :param code: The authorization code.
        :param client: The client.

        :return: The authorization code or None if it does not exist.
        """
        try:
            auth_code = (
                db.session.query(OAuth2AuthorizationCode).filter_by(code=code, client_id=client.client_id).one_or_none()
            )
        except SQLAlchemyError as error:
            LOGGER.error('Failed to query authorization code: %s', error)
            return None
        if not auth_code:
            return None

        if not auth_code.is_expired():
            self.delete_authorization_code(auth_code)
            return None

        return auth_code

    def delete_authorization_code(self, authorization_code):
        """
        Delete an authorization code

        :param authorization_code: the authorization code to delete

        :return: True if the authorization code was deleted, False otherwise
        """
        if not authorization_code:
            return False
        try:
            db.session.query(OAuth2AuthorizationCode).filter_by(id=authorization_code.id).delete()
            db.session.commit()
            return True
        except SQLAlchemyError as error:
            LOGGER.error('Failed to delete authorization code: %s,error info: %s', authorization_code.code, error)
            return False

    def authenticate_user(self, authorization_code):
        """
        Authenticate user from authorization code

        :param authorization_code: authorization code

        :return: user object
        """
        if not authorization_code:
            return None
        try:
            user = db.session.query(User).filter_by(username=authorization_code.username).one_or_none()
        except SQLAlchemyError as error:
            LOGGER.error('Failed to query user: %s', error)
            return None
        return user


class PasswordGrant(grants.ResourceOwnerPasswordCredentialsGrant):
    """
    Password Grant type
    """

    def authenticate_user(self, username, password):
        """
        Authenticate the user and return the user object.

        :param username: The username of the user.
        :param password: The password of the user.
        """
        try:
            user = User.query.filter_by(username=username).one_or_none()
        except SQLAlchemyError as error:
            LOGGER.error('Failed to query user: %s', error)
            return None
        if not user or not user.check_password(password):
            return None

        return user


class RefreshTokenGrant(grants.RefreshTokenGrant):
    """
    Refresh Token Grant type
    """

    def authenticate_refresh_token(self, refresh_token: str):
        """
        Authenticate the refresh token.

        :param refresh_token: Refresh token
        """
        try:
            token = OAuth2Token.query.filter_by(refresh_token=refresh_token).one_or_none()
            if token and token.is_revoked():
                return token
        except SQLAlchemyError as error:
            LOGGER.error('Failed to query refresh token: %s', error)

        return None

    def authenticate_user(self, credential: OAuth2Token):
        """
        Authenticate the user using the credential.

        :param credential: The credential to use for authentication token.
        """
        try:
            user = User.query.filter_by(id=credential.user_id).one_or_none()
        except SQLAlchemyError as error:
            LOGGER.error('Failed to query user: %s', error)
            user = None

        return user

    def revoke_old_credential(self, credential: OAuth2Token):
        """
        Revoking the previously issued token

        :param credential: OAuth2Token instance
        """
        try:
            credential.revoked = True
            db.session.add(credential)
            db.session.commit()
            return True
        except SQLAlchemyError as error:
            LOGGER.error('Failed to revoke token: %s', error)
            return False


class OIDC:
    def generate_user_info(self, user, scope):
        user_info = User(id=user.id, name=user.username)
        if "email" in scope:
            user_info.email = user.email
        return user_info

    def exists_nonce(self, nonce, request):
        try:
            oauth_code = OAuth2AuthorizationCode.query.filter_by(client_id=request.client_id, nonce=nonce).one_or_none()
        except SQLAlchemyError as error:
            LOGGER.error('Failed to query authorization code: %s', error)
            return False

        return True if oauth_code else False


class OpenIDCode(OIDC, _OpenIDCode):

    def get_jwt_config(self, grant):
        jwt = deepcopy(JWT_CONFIG)
        jwt["key"] = grant.client.client_secret
        jwt["aud"] = grant.client.client_id
        return jwt

    def generate_user_info(self, user, scope):
        user_info = dict(id=user.id, username=user.username)
        if "email" in scope:
            user_info.email = user.email
        return user_info


class ImplicitGrant(_OpenIDImplicitGrant, OIDC):

    def get_jwt_config(self):
        jwt = deepcopy(JWT_CONFIG)
        jwt["key"] = self.client.client_secret
        jwt["aud"] = self.client.client_id
        return jwt


class HybridGrant(_OpenIDHybridGrant, OIDC):
    def save_authorization_code(self, code, request) -> str:
        """
        Save an authorization code.

        :param client: OAuth2 client
        :param grant_user: User
        :param request: OAuth2Request

        :return: authorization code
        """
        nonce = request.data.get('nonce')
        try:
            if OAuth2AuthorizationCode.query.filter_by(client_id=request.client.client_id, code=code).one_or_none():
                raise OAuth2Error("Authorization code already exists")

            auth_code = OAuth2AuthorizationCode(
                code=code,
                client_id=request.client.client_id,
                redirect_uri=request.redirect_uri,
                scope=request.scope,
                user_id=request.user.id,
                nonce=nonce,
            )
            db.session.add(auth_code)
            db.session.commit()
        except SQLAlchemyError as error:
            LOGGER.error("Failed to create authorization code: %s", error)
            raise OAuth2Error("Failed to save authorization code")

        return code

    def get_jwt_config(self):
        jwt = deepcopy(JWT_CONFIG)
        jwt["key"] = self.client.client_secret
        jwt["aud"] = self.client.client_id
        return jwt
