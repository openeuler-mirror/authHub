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
from flask import g, make_response, request
from oauth2_provider.app import cache
from oauth2_provider.app.core.account import UserProxy
from oauth2_provider.app.serialize.account import AddUserSchema, LoginSchema, ResetPasswordSchema
from oauth2_provider.app.views import login_require, validate_request
from vulcanus.restful.resp import state
from vulcanus.restful.response import BaseResponse


class AddUser(BaseResponse):
    """
    Interface for register user.
    Restful API: post
    """

    @validate_request(schema=AddUserSchema)
    def post(self, request_body, *args, **kwargs):
        """
        Add user

        Args:
            username (str)
            password (str)
            email (str)

        Returns:
            dict: response body
        """
        register_res = UserProxy().register_user(request_body)
        if register_res != state.SUCCEED:
            return self.response(code=register_res, message="register user failed.")
        return self.response(code=state.SUCCEED)


class Login(BaseResponse):
    """
    Interface for user login.
    Restful API: post
    """

    @validate_request(schema=LoginSchema)
    def post(self, request_body, *args, **kwargs):
        """
        User login

        Args:
            username (str)
            password (str)

        Returns:
            dict: response body
        """
        status_code, user_token = UserProxy().login(request_body)
        if status_code != state.SUCCEED:
            return self.response(code=status_code)
        response = make_response(self.response(code=status_code, data=dict(user_token=user_token)))
        if not request_body["for_validate"]:
            # 30 days expire
            response.set_cookie("Authorization", user_token, 60 * 60 * 24 * 30)
            cache.set(request_body["username"] + "-token", user_token)
            cache.expire(request_body["username"] + "-token", 60 * 60 * 24 * 30)
        return response


class ManagerLogin(BaseResponse):
    """
    Interface for user login.
    Restful API: post
    """

    @validate_request(schema=LoginSchema)
    def post(self, request_body, *args, **kwargs):
        """
        User login

        Args:
            username (str)
            password (str)

        Returns:
            dict: response body
        """
        status_code, user_token = UserProxy().manager_login(request_body)
        if status_code != state.SUCCEED:
            return self.response(code=status_code)
        user_token = "bearer " + user_token
        response = make_response(self.response(code=status_code, data=dict(user_token=user_token)))
        response.set_cookie('Authorization', '', expires=0)
        cache.set(request_body["username"] + "-manager-token", user_token)
        cache.expire(request_body["username"] + "-manager-token", 60 * 60 * 2)
        return response


class ChangePassword(BaseResponse):
    """
    Interface for user change password.
    Restful API: post
    """

    @login_require
    @validate_request(schema=ResetPasswordSchema)
    def post(self, request_body, *args, **kwargs):
        reset_res = UserProxy().reset_password(request_body)
        return self.response(code=reset_res)


class Logout(BaseResponse):
    """
    Interface for logout.
    Restful API: post
    """

    @login_require
    def get(self, *args, **kwargs):
        """
        Logout.

        Returns:
            dict: response body
        """
        # authhub manager user does not process application logout callback operations
        if g.is_manage_user:
            cache.delete(g.username + "-manager-token")
            return make_response(self.response(code=state.SUCCEED))
        logout_res = UserProxy().application_logout()
        if logout_res != state.SUCCEED:
            return self.response(code=logout_res)
        cache.delete(g.username + "-token")
        response = make_response(self.response(code=state.SUCCEED))
        response.set_cookie("Authorization", "", 0)
        response.status_code = 302
        response.headers['Location'] = request.args.get('redirect_uri')
        return response
