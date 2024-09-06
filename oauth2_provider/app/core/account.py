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
import base64
from typing import Tuple

import sqlalchemy
from flask import g
from oauth2_provider.app.constant import secret
from oauth2_provider.app.core.token import jwt_token
from oauth2_provider.database.table import LoginRecords, ManageUser, OAuth2Client, OAuth2ClientScopes, OAuth2Token, User
from oauth2_provider.manage import db
from vulcanus.conf import constant
from vulcanus.log.log import LOGGER
from vulcanus.restful.resp.state import (
    DATA_EXIST,
    DATABASE_INSERT_ERROR,
    DATABASE_QUERY_ERROR,
    DATABASE_UPDATE_ERROR,
    LOGIN_ERROR,
    LOGOUT_ERROR,
    NO_DATA,
    PARTIAL_SUCCEED,
    PASSWORD_ERROR,
    PERMESSION_ERROR,
    REPEAT_DATA,
    SUCCEED,
)
from vulcanus.restful.response import BaseResponse
from werkzeug.security import generate_password_hash


class UserProxy:
    """
    User related table operation
    """

    HEADERS = {"Content-Type": "application/json", "User-Agent": 'authhub'}

    def register_user(self, data) -> str:
        """Register user.

        Args:
            data (dict):
            {
                username (str)
                password (str)
                email (str)
            }

        Returns:
            str: status_code
        """
        username = data.get('username')
        password = data.get('password')
        email = data.get("email")
        try:
            if not self._check_user_not_exist(username):
                LOGGER.error(f"add user failed, username exists: {username}")
                return DATA_EXIST
            self._add_user(username, password, email)
            callback_res = self._register_callback(username)
            if callback_res != SUCCEED:
                return callback_res
            db.session.commit()
            LOGGER.debug("add user succeed.")
        except sqlalchemy.exc.SQLAlchemyError as error:
            LOGGER.error(error)
            LOGGER.error("add user failed.")
            db.session.rollback()
            return DATABASE_INSERT_ERROR
        return SUCCEED

    def _register_callback(self, username: str) -> str:
        res = SUCCEED
        for client in db.session.query(OAuth2Client).distinct(OAuth2Client.client_id).all():
            user_info = self._get_user_info(username, client.client_id)
            for register_callback_uri in client.register_callback_uris:
                response_data = BaseResponse.get_response(
                    method="Post", url=register_callback_uri, data=user_info, header=self.HEADERS
                )
                response_status = response_data.get("label")
                if response_status != SUCCEED:
                    LOGGER.error(f"register redirect failed: {client.client_id}, {username}")
                    res = PARTIAL_SUCCEED
        return res

    def _get_user_info(self, username: str, client_id: str) -> dict:
        """
        Get user info.

        Args:
            username(str): username,
            client_id(str): client id

        Returns:
            dict: user info
        """
        client_scopes = db.session.query(OAuth2ClientScopes).filter_by(username=username, client_id=client_id).one()
        user = db.session.query(User).filter_by(username=username).one()
        user_info = dict()
        # user scope, e.g. ["email","username","openid","offline_access"]
        scopes = client_scopes.scopes.split()
        if "username" in scopes:
            user_info["username"] = user.username
        if "email" in scopes:
            user_info["email"] = user.email
        return user_info

    def _check_user_not_exist(self, username: str) -> bool:
        query_res = db.session.query(User).filter_by(username=username).count()
        if query_res != 0:
            return False
        return True

    def _add_user(self, username: str, password: str, email: str):
        """
        Setup user

        Args:
            data(dict): parameter, e.g.
                {
                    "username": "xxx",
                    "password": "xxx",
                    "email": "xxx@xxx.com"
                }
        """
        password_hash = User.hash_password(password)
        user = User(username=username, password=password_hash, email=email)
        db.session.add(user)

    def manager_login(self, data) -> Tuple[str, str]:
        """
        Check user login

        Args:
            data(dict): parameter, e.g.
                {
                    "username": "xxx",
                    "password": "xxxxx
                }

        Returns:
            Tuple[str, dict]
            str: status code
            dict: user_token, jwt token generated after validation
        """
        login_res = self._login(self, is_manage_user=True, data=data)
        if login_res != SUCCEED:
            return login_res, ""
        # 2 hours expire
        user_token = jwt_token.generate_token(secret, 60 * 60 * 2, data.get('username'))
        return SUCCEED, user_token

    def login(self, data) -> Tuple[str, str]:
        """
        Check user login

        Args:
            data(dict): parameter, e.g.
                {
                    "username": "xxx",
                    "password": "xxxxx
                }

        Returns:
            str: status code
            user_token: jwt token generated after validation
        """
        login_res = self._login(self, is_manage_user=False, data=data)
        if login_res != SUCCEED:
            return login_res, ""
        # 5 days expire
        user_token = jwt_token.generate_token(secret, 60 * 60 * 24 * 5, data.get('username'))
        return SUCCEED, user_token

    def _login(self, is_manage_user: bool, data: dict) -> str:
        username = data.get('username')
        password = data.get('password')
        try:
            if is_manage_user:
                user = db.session.query(ManageUser).filter_by(username=username).one_or_none()
            else:
                user = db.session.query(User).filter_by(username=username).one_or_none()
            if not user:
                LOGGER.error("login with unknown username.")
                return LOGIN_ERROR

            res = user.check_password(password)
            if not res:
                LOGGER.error("login with wrong password")
                return PASSWORD_ERROR
        except sqlalchemy.orm.exc.MultipleResultsFound as error:
            LOGGER.error(error)
            LOGGER.error(f"user should be unique: {username}")
            return REPEAT_DATA
        except sqlalchemy.exc.SQLAlchemyError as error:
            LOGGER.error(error)
            LOGGER.error("user login failed.")
            return DATABASE_QUERY_ERROR

    def reset_password(self, data) -> str:
        """
        Reset user password. Only administrators have the permission.

        Args:
            data(dict): parameter, e.g.
                {
                    "username": "xxx",
                }

        Returns:
            str: status code
        """

        username = data.get('username')
        try:
            if not db.session.query(ManageUser).filter_by(username=g.username).one_or_none():
                return PERMESSION_ERROR

            change_user = db.session.query(User).filter_by(username=username).one_or_none()
            if not change_user:
                return NO_DATA
            change_user.password = generate_password_hash(constant.DEFAULT_PASSWORD)
            db.session.commit()
            LOGGER.debug("reset password succeed")
            return SUCCEED
        except sqlalchemy.orm.exc.MultipleResultsFound as error:
            LOGGER.error(error)
            return REPEAT_DATA
        except sqlalchemy.exc.SQLAlchemyError as error:
            LOGGER.error(error)
            LOGGER.error("reset password fail")
            db.session.rollback()
            return DATABASE_UPDATE_ERROR

    def application_logout(self) -> Tuple[str, str]:
        """
        Logout the user for all related applicatioins.

        Returns:
            Tuple: [status code, username]
        """
        try:
            callback_res = self._logout_callback(g.username)
            if callback_res != SUCCEED:
                return callback_res
            db.session.query(OAuth2Token).filter_by(username=g.username).delete(synchronize_session=False)
            db.session.query(LoginRecords).filter_by(username=g.username).delete(synchronize_session=False)
            db.session.commit()
        except sqlalchemy.exc.SQLAlchemyError as error:
            LOGGER.error(error)
            LOGGER.error("logout failed")
            db.session.rollback()
            return LOGOUT_ERROR
        return SUCCEED

    def _logout_callback(self, username: str) -> str:
        res = SUCCEED
        # verify the request
        login_records = db.session.query(LoginRecords).filter_by(username=username).all()
        if not login_records:
            LOGGER.debug(f"{username} not in login state.")
            return SUCCEED

        for login_record in login_records:
            client = db.session.query(OAuth2Client).filter_by(client_id=login_record.client_id).one_or_none()
            if not client:
                LOGGER.error(f"get client info failed for client: {login_record.client_id}, please check")
                continue
            # encrypt info: {client_id: client_secret}
            encrypted_data = str({login_record.client_id: client.client_secret})
            encrypted_data = encrypted_data.encode('utf-8')
            encoded_data = base64.b64encode(encrypted_data)
            encrypted_string = encoded_data.decode('utf-8')
            logout_callback_uris = login_record.logout_url.split(",")
            for logout_callback_uri in logout_callback_uris:
                response_data = BaseResponse.get_response(
                    method="Post",
                    url=logout_callback_uri,
                    data=dict(username=username, encrypted_string=encrypted_string),
                    header=self.HEADERS,
                )
                response_status = response_data.get("label")
                if response_status != SUCCEED:
                    LOGGER.error(
                        f"logout for '{logout_callback_uri}' failed: {login_record.client_id}, {login_record.username}"
                    )
                    res = PARTIAL_SUCCEED
        return res
