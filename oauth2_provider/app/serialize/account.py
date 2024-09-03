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
"""
Time:
Author:
Description: For account related interfaces
"""
from marshmallow import Schema, fields, validate
from vulcanus.restful.serialize.validate import ValidateRules


class AddUserSchema(Schema):
    """
    validators for parameter of /oauth2/register
    """

    username = fields.String(required=True, validate=ValidateRules.account_name_check)
    password = fields.String(required=True, validate=ValidateRules.account_password_check)
    email = fields.Email(required=True)


class LoginSchema(Schema):
    """
    validators for parameter of /oauth2/login or /oauth2/manager-login
    """

    username = fields.String(required=True, validate=validate.Length(min=5, max=20))
    password = fields.String(required=True, validate=validate.Length(min=6, max=20))
    for_validate = fields.Boolean(required=False, missing=False)


class ResetPasswordSchema(Schema):
    """
    validators for parameter of /oauth2/password
    """

    username = fields.String(required=True, validate=validate.Length(min=5, max=20))


class LogoutSchema(Schema):
    """
    validators for parameter of /oauth2/logout
    """

    token = fields.String(required=True, validate=validate.Length(min=1, max=255))
    client_id = fields.String(required=True, validate=validate.Length(min=1, max=48))
