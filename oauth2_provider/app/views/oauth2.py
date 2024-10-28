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
import json
import time
from datetime import datetime
from urllib.parse import quote

from authlib.integrations.flask_oauth2 import AuthorizationServer, ResourceProtector
from authlib.oauth2.rfc6749.errors import (
    MissingAuthorizationError,
    OAuth2Error,
    UnsupportedResponseTypeError,
    UnsupportedTokenTypeError,
)
from authlib.oauth2.rfc6750.errors import InsufficientScopeError, InvalidTokenError
from flask import g, redirect, request
from jwt.exceptions import ExpiredSignatureError
from sqlalchemy.exc import SQLAlchemyError
from vulcanus.log.log import LOGGER
from vulcanus.restful.resp import state
from vulcanus.restful.response import BaseResponse
from werkzeug.utils import cached_property, import_string

from oauth2_provider.app import cache
from oauth2_provider.app.constant import secret
from oauth2_provider.app.core.token import jwt_token
from oauth2_provider.app.serialize.oauth2 import OauthTokenIntrospectSchema, OauthTokenSchema, RefreshTokenSchema
from oauth2_provider.app.views import login_require, validate_request
from oauth2_provider.database.table import LoginRecords, OAuth2Client, OAuth2ClientScopes, OAuth2Token
from oauth2_provider.manage import db


class OAuth2:

    @cached_property
    def server(self) -> AuthorizationServer:
        """
        All in one endpoints. This property is created automaticly
        if you have implemented all the getters and setters.

        """
        try:
            authorization = import_string("oauth2_provider.manage.authorization")
            return authorization
        except ImportError:
            raise NotImplementedError("You must implement the authorization property")

    @cached_property
    def oauth_validate(self) -> ResourceProtector:
        """
        oAuth2 validation endpoints. This property is created automaticly
        """
        try:
            validate = import_string("oauth2_provider.manage.require_oauth")
            return validate
        except ImportError:
            raise NotImplementedError("You must implement the require_oauth property")

    def redirect(self, url, **kwargs):
        return redirect(url)


class OauthorizeView(BaseResponse, OAuth2):
    """
    oauth2 authorize view
    """

    redirect_error_uri = '/authhub/oauth/authorize/error'
    authorization_confirm_uri = '/authhub/oauth/authorize/confirm'
    login_uri = "/authhub/oauth/authorize/login"

    def has_user_authorization(self, auth_request):
        try:
            oauth_client_scope = OAuth2ClientScopes.query.filter_by(
                client_id=auth_request.client.client_id, username=g.username
            ).one_or_none()
            if not oauth_client_scope:
                return False
            if not oauth_client_scope.is_expired():
                db.session.delete(oauth_client_scope)
                db.session.commit()
                return False

        except SQLAlchemyError as error:
            LOGGER.error(error)
            return False

        return True

    def _validate_token(self, token):
        try:
            token_info = jwt_token.decode(token=token, secret=secret)
            g.username = token_info["sub"]
            cache_token = cache.get(token_info["sub"] + "-token")
            if token != cache_token:
                raise ValueError
            return True
        except ExpiredSignatureError as error:
            LOGGER.error("Signature has expired: %s" % token)
            return False
        except ValueError:
            LOGGER.error("It is not a valid token: %s" % token)
            return False

    def get(self):
        auth_request = self.server.create_oauth2_request(request)
        # get grant
        try:
            grant = self.server.get_authorization_grant(auth_request)
        except UnsupportedResponseTypeError as e:
            LOGGER.error("Unsupported response type: %s" % e)
            return self.redirect(self.redirect_error_uri)

        # validate client and redirect uri
        try:
            redirect_uri = grant.validate_authorization_request()
        except OAuth2Error as e:
            LOGGER.error("Oauth2 error by client id: %s" % auth_request.client_id)
            return self.redirect(self.redirect_error_uri)

        # validate login user
        try:
            redirect_url = (
                (request.args.get('redirect_to_url') or self.login_uri)
                + "?authorization_uri="
                + quote(request.full_path)
            )
            if not self._validate_token(request.cookies.get('Authorization')):
                raise InvalidTokenError("Invalid token")

        except (MissingAuthorizationError, UnsupportedTokenTypeError, InvalidTokenError, InsufficientScopeError) as e:
            LOGGER.error("Not login: %s" % e)
            return self.redirect(redirect_url)

        if grant.client.skip_authorization or self.has_user_authorization(auth_request):
            # for example headers: [('Location', uri)]
            status, payload, headers = grant.create_authorization_response(redirect_uri, g.username)
            if "redirect_index" in request.args:
                headers[-1] = ("Location", headers[-1][-1] + "&redirect_index=" + request.args["redirect_index"])
            return self.server.handle_response(status, payload, headers)

        # check if user has already authorized this client
        return self.redirect(self.authorization_confirm_uri)


class OauthTokenView(BaseResponse, OAuth2):
    """
    oauth2 code view
    """

    @validate_request(schema=OauthTokenSchema)
    def post(self, *args, **kwargs):
        """
        Verify the validity of code and return token

        grant_type
            REQUIRED.  Value MUST be set to "authorization_code".

        code
            REQUIRED.  The authorization code received from the authorization server.

        redirect_uri
            REQUIRED, if the "redirect_uri" parameter was included in the
            authorization request as described in Section 4.1.1, and their
            values MUST be identical.

        client_id
            REQUIRED, if the client is not authenticating with the
            authorization server as described in Section 3.2.1.
        """
        response = self.server.create_token_response()
        response_data = json.loads(response.data.decode())
        if response.status_code == 200:
            data = dict(access_token=response_data["access_token"], refresh_token=response_data["refresh_token"])
            if "id_token" in response_data:
                data["id_token"] = response_data["id_token"]
            return self.response(code=state.SUCCEED, data=data)
        LOGGER.error("Validate code failed: %s", response_data["error"])
        return self.response(code=state.AUTH_ERROR, message=response_data["error"])


class OauthRevokeView(BaseResponse, OAuth2):
    """
    oauth2 revoke view
    """

    @login_require
    def post(self):
        return self.server.create_endpoint_response("revocation")


class OauthIntrospectView(BaseResponse):
    """
    oauth2 token introspect view
    """

    @validate_request(schema=OauthTokenIntrospectSchema)
    def post(self, request_body, *args, **kwargs):
        try:
            client = (
                db.session.query(OAuth2Client).filter(OAuth2Client.client_id == request_body["client_id"]).one_or_none()
            )
            if not client:
                return self.response(code=state.PARAM_ERROR)
            token_info = jwt_token.decode(
                token=request_body["token"], secret=client.client_secret, client=client.client_id
            )
            token = (
                db.session.query(OAuth2Token)
                .filter(OAuth2Token.access_token == request_body["token"], OAuth2Token.username == token_info["sub"])
                .one_or_none()
            )
            if not token:
                return self.response(code=state.TOKEN_ERROR)
            if token.client_id != client.client_id:
                return self.response(code=state.TOKEN_ERROR)
            if not LoginRecords.query.filter_by(username=token.username, client_id=client.client_id).one_or_none():

                login_records = LoginRecords(
                    username=token.username,
                    client_id=client.client_id,
                    logout_url=",".join(client.logout_callback_uris),
                    login_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                )
                db.session.add(login_records)
                db.session.commit()
                LOGGER.info(f"Login records successfully: {token_info['sub']},client_id:{client.client_id}")
        except SQLAlchemyError as error:
            LOGGER.error(error)
            return self.response(code=state.DATABASE_QUERY_ERROR)
        except ValueError:
            return self.response(code=state.TOKEN_ERROR)
        except ExpiredSignatureError:
            return self.response(code=state.TOKEN_EXPIRE)

        return self.response(code=state.SUCCEED, data=token_info["sub"])


class RefreshTokenView(BaseResponse):
    """
    refresh oauth2 token
    """

    def _update_token(self, token: OAuth2Token, client: OAuth2Client):
        token.access_token = jwt_token.generate_token(
            secret=client.client_secret,
            user=token.username,
            scope=token.scope,
            client=client.client_id,
            expires_in=token.expires_in,
        )
        token.issued_at = int(time.time())
        token.token_metadata["expires_in"] = token.expires_in
        token.token_metadata["account_token_exp"] = jwt_token.timedelta(token.expires_in)
        db.session.commit()

    @validate_request(schema=RefreshTokenSchema)
    def post(self, request_body, *args, **kwargs):
        try:
            client = OAuth2Client.query.filter_by(client_id=request_body["client_id"]).one_or_none()
            if not client:
                return self.response(code=state.GENERATION_TOKEN_ERROR)

            token = OAuth2Token.query.filter_by(
                refresh_token=request_body["refresh_token"], client_id=request_body["client_id"]
            ).one_or_none()
            if not token:
                return self.response(code=state.TOKEN_ERROR)
            if token.is_revoked() or token.is_expired():
                db.session.delete(token)
                db.session.commit()
                return self.response(code=state.TOKEN_EXPIRE)

            token_info = jwt_token.decode(request_body["refresh_token"], client.client_secret, client.client_id)
            if token_info["sub"] != token.username:
                return self.response(code=state.TOKEN_ERROR)

            self._update_token(token, client)
            LOGGER.info("Token refreshed successfully: %s " % token_info['sub'])
            return self.response(code=state.SUCCEED, data=dict(access_token=token.access_token))
        except (ExpiredSignatureError, ValueError) as error:
            return self.response(code=state.TOKEN_EXPIRE)
        except SQLAlchemyError as error:
            LOGGER.error(error)
            return self.response(code=state.DATABASE_QUERY_ERROR)
