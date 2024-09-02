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
# ******************************************************************************
import ast
from functools import wraps
from urllib.parse import unquote

from flask import g, jsonify, request
from jwt.exceptions import ExpiredSignatureError
from vulcanus.restful.resp import make_response, state
from vulcanus.restful.serialize.validate import validate

from oauth2_provider.app import cache
from oauth2_provider.app.constant import secret
from oauth2_provider.app.core.token import jwt_token


def validate_request(schema=None):
    """
    Validate request parameters.

    :param schema: request parameters schema model
    """

    def validate_request_handle(api):
        @wraps(api)
        def wrapper(*args, **kwargs):
            if not schema:
                return api(*args, **kwargs)

            body = dict()
            if request.method != "GET":
                body = request.get_json() or dict()
            else:
                for key, value in request.args.items():
                    if (value.startswith("[") or value.startswith("{")) and (
                        value.endswith("]") or value.endswith("}")
                    ):
                        body[key] = ast.literal_eval(value)
                    elif (value.startswith("%5B") and value.endswith("%5D")) or (
                        value.startswith("%7B") and value.endswith("%7D")
                    ):
                        body[key] = ast.literal_eval(unquote(value))
                    else:
                        body[key] = value
            request_args, errors = validate(schema, body, True)
            if errors:
                return jsonify(make_response(label=state.PARAM_ERROR))

            return api(request_body=request_args, *args, **kwargs)

        return wrapper

    return validate_request_handle


def login_require(api):
    @wraps(api)
    def wrapper(*args, **kwargs):
        token = request.headers.get('Authorization') or request.cookies.get('Authorization')
        if not token:
            return jsonify(make_response(label=state.TOKEN_ERROR))
        try:
            is_manage_user = token.startswith("bearer ")
            if is_manage_user:
                token_info = jwt_token.decode(token=token.split(None, 1)[-1], secret=secret)
            else:
                token_info = jwt_token.decode(token=token, secret=secret)
            # check cache token
            cache_token_key = token_info["sub"] + "-manager-token" if is_manage_user else token_info["sub"] + "-token"
            cache_token = cache.get(cache_token_key)
            if not cache_token or cache_token != token:
                return jsonify(make_response(label=state.TOKEN_ERROR))

            g.username = token_info["sub"]
            g.is_manage_user = is_manage_user

        except ExpiredSignatureError:
            return jsonify(make_response(label=state.TOKEN_ERROR))
        except ValueError:
            return jsonify(make_response(label=state.TOKEN_ERROR))
        return api(*args, **kwargs)

    return wrapper
