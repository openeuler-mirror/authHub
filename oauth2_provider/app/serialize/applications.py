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

# marshmallow
from marshmallow import Schema, fields, validate, ValidationError
from vulcanus.restful.serialize.validate import ValidateRules

class Oauth2ClientSchema(Schema):
    """
    validators for parameter of /user/account/change
    """
    client_name = fields.String(required=True)
    client_uri = fields.URL(required=True)
    redirect_uris = fields.List(fields.URL(), required=True)
    skip_authorization = fields.Boolean(default=True)
    register_callback_uris = fields.List(fields.URL())
    logout_callback_uris = fields.List(fields.URL())
    scope = fields.List(
        fields.String(validate=validate.OneOf(['username', 'email', 'openid', 'phone','offline_access'])),
        required=True
    )
    grant_types = fields.List(
        fields.String(
            validate=validate.OneOf(["authorization_code", "client_credentials"])
        ),
        required=True
    )
    response_types = fields.List(
        fields.String(validate=validate.OneOf(['token','code'])),
        required=True
    )
    token_endpoint_auth_method = fields.String(
        required=True, 
        validate=validate.OneOf(["client_secret_basic", "client_secret_post", "none"])
    )


class UpdateOauth2ClientSchema(Schema):
    client_uri = fields.URL(required=True)
    redirect_uris = fields.List(fields.URL(), required=True)
    skip_authorization = fields.Boolean(required=True)
    register_callback_uris = fields.List(fields.URL(), required=True)
    logout_callback_uris = fields.List(fields.URL(), required=True)
    scope = fields.List(
        fields.String(validate=validate.OneOf(['username', 'email', 'openid', 'phone','offline_access'])),
        required=True
    )
    grant_types = fields.List(
        fields.String(
            validate=validate.OneOf(["authorization_code", "client_credentials"])
        ),
        required=True
    )
    response_types = fields.List(
        fields.String(validate=validate.OneOf(['token','code'])),
        required=True
    )
    token_endpoint_auth_method = fields.String(
        required=True, 
        validate=validate.OneOf(["client_secret_basic", "client_secret_post", "none"])
    )

