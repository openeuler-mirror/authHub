#!/usr/bin/python3
# ******************************************************************************
# Copyright (c) Huawei Technologies Co., Ltd. 2021-2021. All rights reserved.
# licensed under the Mulan PSL v2.
# You can use this software according to the terms and conditions of the Mulan PSL v2.
# You may obtain a copy of Mulan PSL v2 at:
#     http://license.coscl.org.cn/MulanPSL2
# THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT, MERCHANTABILITY OR FIT FOR A PARTICULAR
# PURPOSE.
# See the Mulan PSL v2 for more details.
# ******************************************************************************/


from setuptools import find_packages, setup

setup(
    name='authhub',
    version='1.0.0',
    packages=find_packages(),
    install_requires=[
        'marshmallow>=3.13.0',
        'Flask',
        'Flask-RESTful',
        'SQLAlchemy',
        "flask_sqlalchemy",
        "redis",
        "authlib",
    ],
    data_files=[
        ('/etc/aops/conf.d', ['authhub.yml']),
        ('/usr/lib/systemd/system', ["authhub.service"]),
        ("/opt/aops/database", ["oauth2_provider/database/authhub.sql"]),
    ],
    zip_safe=False,
)
