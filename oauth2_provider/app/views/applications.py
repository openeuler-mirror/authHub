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
from flask import request, g
from vulcanus.log.log import LOGGER
from vulcanus.restful.resp import state
from vulcanus.restful.response import BaseResponse
from vulcanus.restful.resp.state import SUCCEED, PERMESSION_ERROR
from oauth2_provider.app.views import validate_request, login_require
from oauth2_provider.app.core.applications import ApplicationProxy
from oauth2_provider.app.serialize.applications import Oauth2ClientSchema, UpdateOauth2ClientSchema


class ApplicationsView(BaseResponse):
    """
    Application management views
    """

    @login_require
    def get(self):
        status_code, applications = ApplicationProxy().get_all_applications(g.username)
        ret_data = {
            "number": len(applications),
            "applications": applications
        }
        return self.response(code=status_code, data=ret_data)


class ApplicationsRegisteView(BaseResponse):
    """
    Application registration views
    """

    @login_require
    @validate_request(schema=Oauth2ClientSchema)
    def post(self, request_body, **params):
        request_body['username'] = g.username
        status_code, application = ApplicationProxy().create_application(request_body)
        return self.response(code=status_code, data=application)


class ApplicationsDetailView(BaseResponse):
    """
    Application detail management views
    """

    @login_require
    def get(self, client_id):
        status_code, application = ApplicationProxy().get_one_application(
            client_id=client_id,
            username=g.username
        )
        return self.response(code=status_code, data=application)

    @login_require
    @validate_request(schema=UpdateOauth2ClientSchema)
    def put(self, client_id, request_body, **params):
        status_code = ApplicationProxy().update_one_application(
            username=g.username,
            client_id=client_id,
            data=request_body
        )
        if status_code != SUCCEED:
            return self.response(code=status_code, data=dict())
        else:
            status_code, application = ApplicationProxy().get_one_application(
                client_id=client_id,
                username=g.username
            )
            return self.response(code=status_code, data=application)

    @login_require
    def delete(self, client_id):
        status_code = ApplicationProxy().delete_one_application(
            client_id=client_id,
            username=g.username
        )
        return self.response(code=status_code)

