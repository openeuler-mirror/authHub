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
from authlib.integrations.flask_oauth2 import AuthorizationServer, ResourceProtector
from authlib.integrations.sqla_oauth2 import (
    create_query_client_func,
    create_revocation_endpoint,
    create_save_token_func,
)
from authlib.oauth2.rfc6749 import grants
from authlib.oauth2.rfc7636 import CodeChallenge
from flask import Flask
from flask.blueprints import Blueprint
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy
from vulcanus.database.proxy import RedisProxy
from werkzeug.utils import import_string

from oauth2_provider.app.settings import configuration


def database_connect():
    host, port, database = configuration.mysql.host, configuration.mysql.port, configuration.mysql.database
    if all([configuration.mysql.password, configuration.mysql.username]):
        username, password = configuration.mysql.username, configuration.mysql.password
        return f"mysql+pymysql://{username}:{password}@{host}:{port}/{database}"

    return f'mysql+pymysql://@{host}:{port}/{database}'


def config_oauth(application, database, authorization: AuthorizationServer, require_oauth: ResourceProtector):
    from oauth2_provider.app.core.grant import (
        AuthorizationCodeGrant,
        HybridGrant,
        ImplicitGrant,
        OpenIDCode,
        PasswordGrant,
        RefreshTokenGrant,
    )
    from oauth2_provider.app.core.validator import JWTBearerTokenValidator
    from oauth2_provider.database.table import OAuth2Client, OAuth2Token

    query_client = create_query_client_func(database.session, OAuth2Client)
    save_token = create_save_token_func(database.session, OAuth2Token)
    authorization.init_app(application, query_client=query_client, save_token=save_token)

    # support all grants
    authorization.register_grant(grants.ImplicitGrant)
    authorization.register_grant(grants.ClientCredentialsGrant)
    authorization.register_grant(
        AuthorizationCodeGrant, [OpenIDCode(require_nonce=True), CodeChallenge(required=False)]
    )
    authorization.register_grant(PasswordGrant)
    authorization.register_grant(RefreshTokenGrant)
    authorization.register_grant(ImplicitGrant)
    authorization.register_grant(HybridGrant)

    # support revocation
    revocation_cls = create_revocation_endpoint(database.session, OAuth2Token)
    authorization.register_endpoint(revocation_cls)
    # register token validator
    require_oauth.register_token_validator(JWTBearerTokenValidator())


def init_app(name):
    """
    init flask app
    """

    app = Flask(__import__(name).__name__)
    app.config.from_mapping(
        {
            'SQLALCHEMY_DATABASE_URI': database_connect(),
            'SQLALCHEMY_TRACK_MODIFICATIONS': False,
            "REFRESH_TOKEN_EXPIRES_IN": 60 * 60 * 24 * 30,  # 30 days
            "TOKEN_EXPIRES_IN": 60 * 60 * 24 * 7,  # 7 days
            "OAUTH2_SCOPES_SUPPORTED": ["openid", "email", "offline_access", "username", "phone"],
            "OAUTH2_ACCESS_TOKEN_GENERATOR": "oauth2_provider.app.core.token.jwt_token",
            "OAUTH2_REFRESH_TOKEN_GENERATOR": "oauth2_provider.app.core.token.jwt_token",
        }
    )
    db = SQLAlchemy(app)
    return app, db


def register_url(app):
    def register_blue_point(urls):
        api = Api()
        for view, url in urls:
            api.add_resource(view, url, endpoint=view.__name__)
        return api

    try:
        urls = import_string("oauth2_provider.urls.URLS")
    except ImportError:
        raise ImportError("Can't import urls")
    # url routing address of the api service
    # register the routing address into the blueprint
    if urls:
        api = register_blue_point(urls)
        api.init_app(app)
        app.register_blueprint(Blueprint('manager', __name__))


def connect_redis():
    if not RedisProxy.redis_connect:
        RedisProxy()
    return RedisProxy.redis_connect


cache = connect_redis()


__all__ = ["config_oauth", "init_app", "register_url", "cache"]
