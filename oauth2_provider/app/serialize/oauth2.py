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
from marshmallow import Schema, fields, validate


class OauthTokenSchema(Schema):
    """
    oauth2 token schema
    """

    grant_type = fields.String(required=True, validate=validate.Length(min=1))
    code = fields.String(required=True, validate=validate.Length(min=1))
    redirect_uri = fields.String(required=True, validate=validate.Length(min=1))
    client_id = fields.String(required=True, validate=validate.Length(min=1))


class OauthTokenIntrospectSchema(Schema):
    """
    oauth2 token introspect schema
    """

    token = fields.String(required=True, validate=validate.Length(min=1))
    client_id = fields.String(required=True, validate=validate.Length(min=1))


class RefreshTokenSchema(Schema):
    """
    oauth2 refresh token schema
    """

    refresh_token = fields.String(required=True, validate=validate.Length(min=1))
    client_id = fields.String(required=True, validate=validate.Length(min=1))
