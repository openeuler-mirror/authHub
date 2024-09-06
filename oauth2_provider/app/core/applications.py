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
import time
from copy import deepcopy
from typing import Tuple
import sqlalchemy
import sqlalchemy.exc
from werkzeug.security import gen_salt
from authlib.common.encoding import json_loads, json_dumps
from vulcanus.conf import constant
from vulcanus.log.log import LOGGER
from vulcanus.restful.resp.state import (
    NO_DATA,
    DATA_EXIST,
    DATABASE_INSERT_ERROR,
    DATABASE_QUERY_ERROR,
    DATABASE_UPDATE_ERROR,
    DATABASE_DELETE_ERROR,
    SUCCEED,
)

from oauth2_provider.manage import db
from oauth2_provider.database.table import OAuth2Client


class ApplicationProxy:
    """
    Application related table operation
    """

    def create_application(self, data: dict) -> str:
        client_id = gen_salt(24)
        client_name = data.get('client_name')
        client = OAuth2Client(client_id=client_id, username=data.get('username'))
        client.username = data.get('username')
        client.client_id_issued_at = int(time.time())
        client.app_name = client_name
        scopes_set = set({"username", "email", "openid", "phone", "offline_access"})
        for scope_item in data.get('scope', []):
            scopes_set.add(scope_item)
        client.set_client_metadata(
            {
                "client_name": data.get('client_name'),
                "client_uri": data.get('client_uri'),
                "skip_authorization": data.get('skip_authorization'),
                "register_callback_uris": data.get('register_callback_uris'),
                "logout_callback_uris": data.get('logout_callback_uris'),
                "redirect_uris": data.get('redirect_uris', []),
                "scope": " ".join(scopes_set),
                "grant_types": data.get('grant_types'),
                "response_types": data.get('response_types'),
                "token_endpoint_auth_method": data.get('token_endpoint_auth_method'),
            }
        )
        client.client_secret = gen_salt(48)
        try:
            if not self._check_client_name_not_exist(client_name):
                LOGGER.error(f"create application failed, application exists: {client_name}")
                return DATA_EXIST, dict()
            db.session.add(client)
            db.session.commit()
            LOGGER.debug("create application succeed.")
        except sqlalchemy.exc.SQLAlchemyError as error:
            LOGGER.error(error)
            LOGGER.error("create application failed.")
            db.session.rollback()
            return DATABASE_INSERT_ERROR, dict()
        ret_data = {"client_info": deepcopy(client.client_info), "client_metadata": deepcopy(client.client_metadata)}
        ret_data['client_metadata']['scope'] = ret_data['client_metadata']['scope'].split()
        return SUCCEED, ret_data

    def _check_client_name_not_exist(self, client_name: str):
        query_res = db.session.query(OAuth2Client).filter(OAuth2Client.app_name == client_name).count()
        if query_res:
            return False
        return True

    def _split_by_crlf(self, split_str):
        if not split_str:
            return []
        return [item for item in split_str.splitlines() if item]

    def get_all_applications(self, username: str):
        try:
            applications = db.session.query(OAuth2Client).filter(OAuth2Client.username == username).all()
            applications_info = []
            for application in applications:
                ret_data = {
                    "client_info": deepcopy(application.client_info),
                    "client_metadata": deepcopy(application.client_metadata),
                }
                ret_data['client_metadata']['scope'] = ret_data['client_metadata']['scope'].split()
                applications_info.append(ret_data)
        except sqlalchemy.exc.SQLAlchemyError as error:
            LOGGER.error(error)
            LOGGER.error("get all accounts info failed")
            return DATABASE_QUERY_ERROR, []
        return SUCCEED, applications_info

    def get_one_application(self, client_id: str, username: str):
        try:
            application = (
                db.session.query(OAuth2Client)
                .filter(OAuth2Client.client_id == client_id, OAuth2Client.username == username)
                .one_or_none()
            )
            if not application:
                LOGGER.info(f'''no application refer to this client_id {client_id}, this username  {username}''')
                return NO_DATA, dict()
            application_info = {
                "client_info": deepcopy(application.client_info),
                "client_metadata": deepcopy(application.client_metadata),
            }
            application_info['client_metadata']['scope'] = application_info['client_metadata']['scope'].split()
        except sqlalchemy.exc.SQLAlchemyError as error:
            LOGGER.error(error)
            LOGGER.error("get one application info failed")
            return DATABASE_QUERY_ERROR, dict()
        return SUCCEED, application_info

    def update_one_application(self, username: str, client_id: str, data: dict):
        try:
            scopes_set = set({"username", "email", "openid", "phone", "offline_access"})
            for scope_item in data.get('scope', []):
                scopes_set.add(scope_item)
            data['scope'] = " ".join(scopes_set)
            application = (
                db.session.query(OAuth2Client)
                .filter(OAuth2Client.client_id == client_id, OAuth2Client.username == username)
                .one()
            )
            if not application:
                return DATABASE_UPDATE_ERROR
            metadata = application.client_metadata
            metadata.update(data)
            ret = (
                db.session.query(OAuth2Client)
                .filter(OAuth2Client.client_id == client_id, OAuth2Client.username == username)
                .update({'_client_metadata': json_dumps(metadata)})
            )
            db.session.commit()
            if not ret:
                LOGGER.info(f'''no application refer to this client_id {client_id}, this user name {username}''')
                return DATABASE_UPDATE_ERROR
        except sqlalchemy.exc.SQLAlchemyError as error:
            LOGGER.error(error)
            db.session.rollback()
            LOGGER.error("update one application info failed")
            return DATABASE_UPDATE_ERROR
        return SUCCEED

    def delete_one_application(self, username: str, client_id: str):
        try:
            ret = (
                db.session.query(OAuth2Client)
                .filter(OAuth2Client.username == username, OAuth2Client.client_id == client_id)
                .delete()
            )
            if not ret:
                LOGGER.info(f'''no application refer to this client_id {client_id}, this user name {username}''')
                return DATABASE_DELETE_ERROR
            db.session.commit()
        except sqlalchemy.exc.SQLAlchemyError as error:
            LOGGER.error(error)
            db.session.rollback()
            LOGGER.error(f'''delete application error, client id is {client_id}, username is {username}''')
            return DATABASE_DELETE_ERROR
        return SUCCEED
