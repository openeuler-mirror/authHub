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
import os

from authlib.integrations.flask_oauth2 import ResourceProtector
from werkzeug.utils import import_string

from oauth2_provider.app import config_oauth, init_app, register_url


def main(application, database):

    os.environ['AUTHLIB_INSECURE_TRANSPORT'] = "SKIP-HTTPS"
    register_url(application)
    try:
        authorization_server = import_string("oauth2_provider.app.core.server.AuthorizationServer")
    except ImportError:
        raise NotImplementedError("Authorization server not implemented")

    _authorization = authorization_server()
    _require_oauth = ResourceProtector()
    config_oauth(application=application, database=database, authorization=_authorization, require_oauth=_require_oauth)
    return _authorization, _require_oauth


app, db = init_app(name="oauth2_provider")
authorization, require_oauth = main(app, db)
