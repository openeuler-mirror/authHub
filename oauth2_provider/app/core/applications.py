from typing import Tuple
import time
from copy import deepcopy

import sqlalchemy
import sqlalchemy.exc
from werkzeug.security import gen_salt
from authlib.common.encoding import json_loads, json_dumps
from vulcanus.conf import constant
from vulcanus.log.log import LOGGER
from vulcanus.restful.resp.state import (
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
        """create application.
        Args:
            data (dict):

            {

            }

        Returns:
            str: status_code
        """
        client_id = gen_salt(24)
        client_name = data.get('client_name')
        client = OAuth2Client(client_id=client_id, username=data.get('username'))
        client.username = data.get('username')
        client.client_id_issued_at = int(time.time())
        client.app_name = data.get('client_name')
        scopes_set = set(["username", "email", "openid", "phone", "offline_access"])
        for scope_item in data.get('scope', []):
            scopes_set.add(scope_item)
        client.set_client_metadata({
            "client_name": data.get('client_name'),
            "client_uri": data.get('client_uri'),
            "skip_authorization": data.get('skip_authorization'), 
            "register_callback_uris": data.get('register_callback_uris'),
            "logout_callback_uris": data.get('logout_callback_uris'),
            "redirect_uris": data.get('redirect_uris', []),
            "scope": " ".join(list(scopes_set)),
            "grant_types": data.get('grant_types'),
            "response_types": data.get('response_types'),
            "token_endpoint_auth_method": data.get('token_endpoint_auth_method')
        })
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
        ret_data = {
            "client_info": deepcopy(client.client_info), 
            "client_metadata": deepcopy(client.client_metadata)
        }
        ret_data['client_metadata']['scope'] = ret_data['client_metadata']['scope'].split()
        return SUCCEED, ret_data

    def _check_client_name_not_exist(self, client_name: str):
        query_res = db.session.query(OAuth2Client).filter(OAuth2Client.app_name == client_name).count()
        if query_res:
            return False
        return True

    def _split_by_crlf(self, s):
        if not s:
            return []
        return [v for v in s.splitlines() if v]
    
    def get_all_applications(self, username: str):
        """Get all applications
        Returns:
            Tuple[str, list]: status_code, applications_info
        """
        try:
            applications = db.session.query(OAuth2Client).filter(
                OAuth2Client.username==username
            ).all()
            applications_info = []
            for application in applications:
                ret_data = {
                    "client_info": deepcopy(application.client_info), 
                    "client_metadata": deepcopy(application.client_metadata)
                }
                ret_data['client_metadata']['scope'] = ret_data['client_metadata']['scope'].split()
                applications_info.append(ret_data)
        except sqlalchemy.exc.SQLAlchemyError as error:
            LOGGER.error(error)
            LOGGER.error("get all accounts info failed")
            return DATABASE_QUERY_ERROR, []
        return SUCCEED, applications_info
  
    def get_one_application(self, client_id: str, username: str):
        """Get one application
            data (dict):
            {
                client_name = fields.String(required=True)
                client_uri = fields.String(required=True)
                skip_auth = fields.String(required=True)
                register_callback_uri = fields.String(required=True)
                allowed_scope = fields.String(required=True)
                redirect_uris = fields.String(required=True)
                allowed_grant_types = fields.String(required=True)
                allowed_responses_types = fields.String(required=True)
                token_endpoint_auth_method = fields.String(required=True)
            }
        Returns:
            Tuple[str, dict]: status_code, application_info
        """
        try:
            application = db.session.query(OAuth2Client).filter(
                OAuth2Client.client_id==client_id,
                OAuth2Client.username==username
            ).one_or_none()
            if not application:
                LOGGER.info(f'''no application refer to this client_id {client_id}, this username  {username}''')
                return DATABASE_QUERY_ERROR, dict()
            application_info = {
                "client_info": deepcopy(application.client_info),
                "client_metadata": deepcopy(application.client_metadata)
            }
            application_info['client_metadata']['scope'] = application_info['client_metadata']['scope'].split()
        except sqlalchemy.exc.SQLAlchemyError as error:
            LOGGER.error(error)
            LOGGER.error("get one application info failed")
            return DATABASE_QUERY_ERROR, dict()
        return SUCCEED, application_info

    def update_one_application(self, username: str, client_id: str, data: dict):
        """Update one application
        Returns:
            Tuple[str, dict]: status_code, application_info
        """
        try:
            scopes_set = set(["username", "email", "openid", "phone", "offline_access"])
            for scope_item in data.get('scope', []):
                scopes_set.add(scope_item)
            data['scope'] = " ".join(list(scopes_set))
            application = db.session.query(OAuth2Client).filter(
                OAuth2Client.client_id==client_id,
                OAuth2Client.username==username
            ).one()
            metadata = application.client_metadata
            metadata.update(data)
            ret = db.session.query(OAuth2Client).filter(
                    OAuth2Client.client_id==client_id,
                    OAuth2Client.username==username
                ).update({'_client_metadata': json_dumps(metadata)})
            db.session.commit()
            if not ret:
                LOGGER.info(f'''no application refer to this client_id {client_id}, this user name {username}''')
                return DATABASE_UPDATE_ERROR
        except sqlalchemy.exc.SQLAlchemyError as error:
            LOGGER.error(error)
            LOGGER.error("update one application info failed")
            return DATABASE_UPDATE_ERROR
        return SUCCEED

    def delete_one_application(self, username: str, client_id: str):
        """delete one application
        Returns:
            Tuple[str, dict]: status_code
        """
        try:
            ret = db.session.query(OAuth2Client).filter(
                OAuth2Client.username==username, 
                OAuth2Client.client_id==client_id
            ).delete()
            if not ret:
                LOGGER.info(f'''no application refer to this client_id {client_id}, this user name {username}''')
                return DATABASE_DELETE_ERROR
            db.session.commit()
        except sqlalchemy.exc.SQLAlchemyError as error:
            LOGGER.error(error)
            LOGGER.error(f'''delete application error, client id is {client_id}, username is {username}''')
            return DATABASE_DELETE_ERROR
        return SUCCEED

