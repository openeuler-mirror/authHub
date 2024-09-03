#!/usr/bin/python3
# ******************************************************************************
# Copyright (c) Huawei Technologies Co., Ltd. 2021-2023. All rights reserved.
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

from authlib.common.encoding import json_dumps, json_loads
from authlib.integrations.sqla_oauth2 import OAuth2AuthorizationCodeMixin, OAuth2ClientMixin, OAuth2TokenMixin
from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import Integer, String, Text
from werkzeug.security import check_password_hash, generate_password_hash

from oauth2_provider.manage import db


class ManageUser(db.Model):

    __tablename__ = 'manage_user'

    id = Column(Integer, primary_key=True)
    username = Column(String(36), unique=True, nullable=False)
    password = Column(String(255), nullable=False)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    @staticmethod
    def hash_password(password):
        return generate_password_hash(password)


class User(db.Model):

    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    username = Column(String(36), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    email = Column(String(40))
    phone = Column(String(11))

    def get_user_id(self):
        return self.id

    def check_password(self, password):
        return check_password_hash(self.password, password)

    @staticmethod
    def hash_password(password):
        return generate_password_hash(password)


class OAuth2Client(db.Model, OAuth2ClientMixin):
    __tablename__ = 'oauth2_client'

    id = Column(Integer, primary_key=True)
    app_name = Column(String(48), unique=True, nullable=False)
    username = Column(String(36), ForeignKey('manage_user.username', ondelete='CASCADE'))

    @property
    def skip_authorization(self):
        return self.client_metadata.get('skip_authorization')

    @property
    def register_callback_uris(self):
        return self.client_metadata.get('register_callback_uris', [])

    @property
    def logout_callback_uris(self):
        return self.client_metadata.get('logout_callback_uris', [])

    def check_grant_type(self, grant_type):
        if grant_type != "refresh_token":
            return grant_type in self.grant_types
        return True


class OAuth2Token(db.Model, OAuth2TokenMixin):
    __tablename__ = 'oauth2_token'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id', ondelete='CASCADE'))
    username = Column(String(36), nullable=False)
    user = relationship('User')
    client_id = Column(
        String(48),
        ForeignKey('oauth2_client.client_id', ondelete='CASCADE'),
        nullable=False,
    )
    client = relationship('OAuth2Client')
    _metadata = Column('token_metadata', Text)
    refresh_token_expires_in = Column(Integer, nullable=False, default=0)

    @property
    def default_scope(self):
        return {"email", "username", "openid", "phone", "offline_access"}

    @property
    def token_metadata(self):
        if 'token_metadata' in self.__dict__:
            return self.__dict__['token_metadata']
        if self._metadata:
            data = json_loads(self._metadata)
            self.__dict__['token_metadata'] = data
            return data

        return dict()

    def set_token_metadata(self, value):
        self._metadata = json_dumps(value)
        if 'token_metadata' in self.__dict__:
            del self.__dict__['token_metadata']

    def is_revoked(self):
        """
        Check whether the token is revoked

        :return: True if the token is revoked, False otherwise
        """
        if self.access_token_revoked_at and self.access_token_revoked_at < int(time.time()):
            return True
        if self.refresh_token_revoked_at and self.refresh_token_revoked_at < int(time.time()):
            return True

        return False

    def get_expires_in(self):
        return self.expires_in

    def is_expired(self):
        if not self.expires_in:
            return False

        expires_at = self.issued_at + self.expires_in
        return expires_at < time.time()


class OAuth2AuthorizationCode(db.Model, OAuth2AuthorizationCodeMixin):
    __tablename__ = 'oauth2_code'

    id = Column(Integer, primary_key=True)
    username = Column(String(50))


class OAuth2ClientScopes(db.Model):
    __tablename__ = 'oauth2_client_scopes'

    id = Column(Integer, primary_key=True)
    username = Column(String(50))
    client_id = Column(Integer, ForeignKey('oauth2_client.id', ondelete='CASCADE'))
    scopes = Column(Text, nullable=False, default="openid profile email")
    client = relationship('OAuth2Client')
    grant_at = Column(Integer, nullable=False, default=lambda: int(time.time()))
    expires_in = Column(Integer, nullable=False, default=0)

    def is_expired(self):
        if not self.expires_in:
            return False
        expires_at = self.grant_at + self.expires_in
        return expires_at < time.time()


class LoginRecords(db.Model):
    __tablename__ = 'login_records'

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50))
    login_time = Column(String(20))
    client_id = Column(String(48), ForeignKey('oauth2_client.client_id', ondelete='CASCADE'))
    logout_url = Column(String(200))
