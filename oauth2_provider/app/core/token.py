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
import json
import time
from datetime import datetime
from datetime import timedelta as _timedelta

import jwt
import pytz
from authlib.oauth2.rfc6750.token import BearerTokenGenerator
from jwt.exceptions import ExpiredSignatureError

from oauth2_provider.manage import app


class JwtTokenGenerator(BearerTokenGenerator):
    """
    jwt token generate

    """

    refresh_token_expires_in = 2592000
    essential_options = {"exp", "sub", "aud"}

    def __init__(self, access_token_generator=None, refresh_token_generator=None, expires_generator=None, alg='HS256'):
        super().__init__(access_token_generator, refresh_token_generator, expires_generator)
        if self.access_token_generator is None:
            self.access_token_generator = self.generate_token
        if self.refresh_token_generator is None:
            self.refresh_token_generator = self.generate_token
        self.alg = alg

    def timedelta(self, seconds: int = 3600) -> int:
        date_span = datetime.now(tz=pytz.timezone('Asia/Shanghai'))
        if seconds:
            date_span = date_span + _timedelta(seconds=seconds)
        time_span = time.strptime(date_span.strftime("%Y-%m-%d %H:%M:%S"), "%Y-%m-%d %H:%M:%S")
        return int(time.mktime(time_span))

    def generate_token(self, secret, expires_in: int, user, client="oauth", **kwargs):

        if not user:
            return ValueError("A unique identifier is missing")
        token_body = dict(
            iat=int(time.time()),
            exp=self.timedelta(expires_in),
            sub=user,
            aud=client,
        )
        for jwt_key in set(kwargs.keys()).intersection(set(["iss", "scope", "jti"])):
            token_body[jwt_key] = kwargs[jwt_key]
        try:
            _jwt_token = jwt.encode(
                token_body,
                secret,
                algorithm=self.alg,
            )
            if isinstance(_jwt_token, bytes):
                _jwt_token = _jwt_token.decode("utf-8")

            return _jwt_token
        except Exception:
            raise ValueError("Token generation failed")

    def generate(self, grant_type, client, user=None, scope=None, expires_in=None, include_refresh_token=True):
        """Generate a bearer token for OAuth 2.0 authorization token endpoint.

        :param client: the client that making the request.
        :param grant_type: current requested grant_type.
        :param user: current authorized user.
        :param expires_in: if provided, use this value as expires_in.
        :param scope: current requested scope.
        :param include_refresh_token: should refresh_token be included.
        :return: Token dict
        """

        scope = self.get_allowed_scope(client, scope)
        if expires_in is None:
            expires_in = app.config.get('TOKEN_EXPIRES_IN') or self._get_expires_in(client, grant_type)

        token = {
            "username": user.username,
            'token_type': 'Bearer',
            'access_token': self.access_token_generator(
                client=client.client_id,
                expires_in=expires_in,
                scope=scope,
                user=user.username,
                secret=client.client_secret,
            ),
        }
        meta = dict(account_token_exp=self.timedelta(expires_in), expires_in=expires_in)
        if scope:
            token['scope'] = scope
        if include_refresh_token:
            refresh_token_expires_in = app.config.get('REFRESH_TOKEN_EXPIRES_IN') or self.refresh_token_expires_in
            token['refresh_token'] = self.refresh_token_generator(
                client=client.client_id,
                expires_in=refresh_token_expires_in,
                scope=scope,
                user=user.username,
                secret=client.client_secret,
            )
            meta['refresh_token_exp'] = self.timedelta(refresh_token_expires_in)
            meta["refresh_token_expires_in"] = refresh_token_expires_in

        token["_metadata"] = json.dumps(meta)
        return token

    def decode(self, token, secret, client="oauth"):
        if not token:
            raise ValueError("Please enter a valid token")

        try:
            claims = jwt.decode(token, secret, algorithms=[self.alg], audience=client)
            if not self.essential_options.issubset(set(claims.keys())):
                raise ValueError("It is not a valid token")

            return claims
        except ExpiredSignatureError:
            raise ExpiredSignatureError("Signature has expired")
        except Exception as error:
            raise ValueError("It is not a valid token")


jwt_token = JwtTokenGenerator()

__all__ = ["jwt_token"]
