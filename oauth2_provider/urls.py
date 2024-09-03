#!/usr/bin/python3
# ******************************************************************************
# Copyright (c) Huawei Technologies Co., Ltd. 2021-2021. All rights reserved.
# licensed under the Mulan PSL v2.
# You can use this software according to the terms and conditions of the Mulan PSL v2.
# You may obtain a copy of Mulan PSL v2 at:
#     http://license.coscl.org.cn/MulanPSL2
# THIS SOFTWARE IS PROVIDED ON AN 'AS IS' BASIS, WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT, MERCHANTABILITY OR FIT FOR A PARTICULAR
# PURPOSE.
# See the Mulan PSL v2 for more details.
# ******************************************************************************/

from oauth2_provider.app.views.oauth2 import (
    OauthIntrospectView,
    OauthorizeView,
    OauthRevokeView,
    OauthTokenView,
    RefreshTokenView,
)

URLS = [
    # oauth2
    (OauthorizeView, "/oauth2/authorize"),
    (OauthTokenView, "/oauth2/token"),
    (OauthRevokeView, "/oauth2/revoke-token"),
    (OauthIntrospectView, "/oauth2/introspect"),
    (RefreshTokenView, "/oauth2/refresh-token"),
]
