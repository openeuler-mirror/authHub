## 1、/oauth2/applications

  + 描述：认证中心下注册管理的所有应用列表

  + Http请求方式：GET

  + 数据提交方式: application/json

  + 请求参数:  **无**

  + 返回体:

    | 参数名  | 类型   | 说明             |
    | ------- | ------ | ---------------- |
    | code    | int    | 状态码           |
    | label   | str    | 标签             |
    | message | str    | 状态码对应的信息 |
    | data    | object | 注册的应用列表   |

  + 返回示例:

    ```json
    {
        "code": "200",
        "data": {
            "applications": [
                {
                    "client_info": {
                        "client_id": "9nO4ioD0Xg8NKQkJDeSp5QHP",
                        "client_id_issued_at": 1732016315,
                        "client_secret": "kJcRKCRS7Q1ElBK4BT6U9JDFYAtgwCvJaXsJeul7RrfqKvkG",
                        "client_secret_expires_at": 0
                    },
                    "client_metadata": {
                        "client_name": "a-ops",
                        "client_uri": "http://172.168.140.44/dashboard",
                        "grant_types": [
                            "authorization_code"
                        ],
                        "logout_callback_uris": [
                            "http://172.168.140.44/accounts/logout/redirect"
                        ],
                        "redirect_uris": [
                            "http://172.168.140.44/user/auth"
                        ],
                        "register_callback_uris": [
                            "http://172.168.140.44/accounts/register"
                        ],
                        "response_types": [
                            "code"
                        ],
                        "scope": [
                            "username",
                            "email",
                            "offline_access",
                            "phone",
                            "openid"
                        ],
                        "skip_authorization": true,
                        "token_endpoint_auth_method": "none"
                    }
                }
            ],
            "number": 3
        },
        "label": "Succeed",
        "message": "operation succeed"
    }
    ```


## 2、/oauth2/applications/register

  + 描述：应用向认证中心注册

  + Http请求方式：POST

  + 数据提交方式: application/json

  + 请求参数: 

    | 参数名                     | 必选  | 类型        | 说明                                                         |
    | -------------------------- | ----- | ----------- | ------------------------------------------------------------ |
    | client_name                | True  | str         | 应用名称                                                     |
    | client_uri                 | True  | str         | 应用的地址                                                   |
    | redirect_uris              | True  | list (str)  | 授权认证成功后跳转的地址                                     |
    | skip_authorization         | False | Bool        | 是否跳过用户点击授权动作                                     |
    | register_callback_uris     | False | list（str） | 认证中心用户注册后，回调应用的地址（携带用户名等，便于应用自行处理） |
    | logout_callback_uris       | False | list (str)  | 用户退出登录后，认证中心回调各应用退出状态的地址             |
    | scope                      | True  | list (str)  | 用户授权时允许获取的信息，目前仅支持（username email openid phone offlie_access） |
    | grant_types                | True  | list (str)  | 客户端授权的方式，仅支持（authorization_code client_credentials） |
    | response_types             | True  | List (str)  | 响应的类型，支持（token  code）                              |
    | token_endpoint_auth_method | True  | List (str)  | token生成的方法，支持（client_secret_basic client_secret_post none），默认传递none |

  + 请求参数示例

    ```json
    {
        "client_name": "test-aaa",
        "client_uri": "https://127.0.0.1",
        "redirect_uris": [
            "https://127.0.0.1"
        ],
        "skip_authorization": true,
        "register_callback_uris": [],
        "logout_callback_uris": [],
        "scope": [
            "email",
            "phone",
            "username",
            "openid",
            "offline_access"
        ],
        "grant_types": [
            "authorization_code"
        ],
        "response_types": [
            "code"
        ],
        "token_endpoint_auth_method": "none"
    }
    ```

  + 返回体:

    | 参数名  | 类型   | 说明             |
    | ------- | ------ | ---------------- |
    | code    | int    | 状态码           |
    | label   | str    | 标签             |
    | message | str    | 状态码对应的信息 |
    | data    | object | 主机状态         |

  + 返回示例:

    ```json
    {
      "code": 0,
      "message": "string",
      "label": "string",
      "data": 
    }
    ```
    
## 3、/oauth2/applications/<string:client_id>

  + 描述：获取应用的详细信息（get请求）、删除应用（delete请求）、修改应用信息（put请求，**具体传参可参考应用注册api**）

  + Http请求方式：GET

  + 数据提交方式: application/json

  + 请求参数: 

    | 参数名    | 必选 | 类型 | 说明   |
    | --------- | ---- | ---- | ------ |
    | client_id | True | str  | 应用id |
    
  + 返回体:

    | 参数名  | 类型   | 说明             |
    | ------- | ------ | ---------------- |
    | code    | int    | 状态码           |
    | label   | str    | 标签             |
    | message | str    | 状态码对应的信息 |
    | data    | object | 应用详细信息     |

  + 返回示例:

    ```json
    {
        "code": "200",
        "data": {
            "client_info": {
                "client_id": "sQi2cF4iXCUAKfPfacmniyeQ",
                "client_id_issued_at": 1742006277,
                "client_secret": "4vG5Xo4zbqH5EpRKk6lQiP7iB8QIzcDVCIgu1E3RUOuamZm6",
                "client_secret_expires_at": 0
            },
            "client_metadata": {
                "client_name": "test-aaa",
                "client_uri": "https://127.0.0.1",
                "grant_types": [
                    "authorization_code"
                ],
                "logout_callback_uris": [],
                "redirect_uris": [
                    "https://127.0.0.1"
                ],
                "register_callback_uris": [],
                "response_types": [
                    "code"
                ],
                "scope": [
                    "openid",
                    "phone",
                    "offline_access",
                    "email",
                    "username"
                ],
                "skip_authorization": true,
                "token_endpoint_auth_method": "none"
            }
        },
        "label": "Succeed",
        "message": "operation succeed"
    }
    ```
    

## 4、/oauth2/authorize

  + 描述：基于oauth2的授权登录，通过请求特定链接地址获取code码

  + Http请求方式：GET

  + 数据提交方式: application/json

  + 请求参数: 

    | 参数名        | 必选  | 类型 | 说明                                                         |
    | ------------- | ----- | ---- | ------------------------------------------------------------ |
    | client_id     | True  | str  | 应用的id                                                     |
    | redirect_uri  | True  | str  | code码回调的地址                                             |
    | scope         | True  | str  | 允许授权获取的信息，多个之间以**空格**隔开                   |
    | response_type | True  | str  | 响应返回的方式                                               |
    | prompt        | False | str  | 控制用户交互行为，可选值为（none login consent select_account） |
    | nonce         | False | str  | 随机字符串，防止重复性请求                                   |

  + 请求参数示例

    ```txt
    http://127.0.0.1/oauth2/authorize?client_id=9nO4ioD0Xg8NKQkJDeSp5QHP&redirect_uri=http://127.0.0.1/user/auth&scope=openid offline_access&response_type=code&prompt=consent&state=235345&nonce=loser
    ```
    
  + 返回体:

    返回时为**302重定向**的返回，重定向地址中携带颁发的**code**码
    
  + 返回示例:

    ```txt
    http://127.0.0.1/user/auth?code=123456
    ```

## 5、/oauth2/token

 + 描述：通过code码换取有效的token

  + Http请求方式：POST

  + 数据提交方式: application/json

  + 请求参数: 

    | 参数名       | 必选 | 类型 | 说明                         |
    | ------------ | ---- | ---- | ---------------------------- |
    | grant_type   | True | str  | 认证类型，默认支持code码模式 |
    | code         | True | str  | code码模式下颁发的临时code   |
    | redirect_uri | True | str  | 应用设置的code回调的地址     |
    | client_id    | True | str  | 应用的id                     |
    
  + 请求参数示例

    ```json
    {
      "client_id": "sQi2cF4iXCUAKfPfacmniyeQ",
      "redirect_uri": "https://127.0.0.1",
      "code": "123456",
      "grant_type": "authorization_code"
    }
    ```
    
  + 返回体:

    | 参数名  | 类型   | 说明                    |
    | ------- | ------ | ----------------------- |
    | code    | int    | 状态码                  |
    | label   | str    | 标签                    |
    | message | str    | 状态码对应的信息        |
    | data    | object | 认证中心颁发的应用token |

  + 返回示例:

    ```json
    {
      "code": 200,
      "label": "Succeed",
      "message": "operation succeed",
        "data": {
            "access_token": "str",
          	"refresh_token":"str",
          	"id_token":"str"
        }
    }
    ```

## 6、/oauth2/revoke-token

 + 描述：客户端主动撤销令牌

  + Http请求方式：POST

  + 数据提交方式: application/json

  + 请求参数:  **无**

  + 返回体:

    | 参数名  | 类型 | 说明             |
    | ------- | ---- | ---------------- |
    | code    | int  | 状态码           |
    | label   | str  | 标签             |
    | message | str  | 状态码对应的信息 |
    
  + 返回示例:

    ```json
    {
      "code": 200,
      "label": "Succeed",
      "message": "operation succeed"
    }
    ```

## 7、/oauth2/introspect

 + 描述：客户端验证token的有效性，是否由认证中心颁发

  + Http请求方式：POST

  + 数据提交方式: application/json

  + 请求参数: 

    | 参数名    | 必选 | 类型 | 说明                        |
    | --------- | ---- | ---- | --------------------------- |
    | client_id | True | str  | 应用id                      |
    | token     | True | str  | 认证中心颁发给客户端的token |

  + 请求参数示例

    ```json
    {
      ”client_id“: "sQi2cF4iXCUAKfPfacmniyeQ",
      "token": "sQi2cF4iXCUAKfPfacmniyeQsQi2cF4iXCUAKfPfacmniyeQsQi2cF4iXCUAKfPfacmniyeQsQi2cF4iXCUAKfPfacmniyeQ"
    }
    ```

  + 返回体:

    | 参数名  | 类型 | 说明             |
    | ------- | ---- | ---------------- |
    | code    | int  | 状态码           |
    | label   | str  | 标签             |
    | message | str  | 状态码对应的信息 |
    | data    | str  | 用户名           |

  + 返回示例:

    ```json
    {
      "code": 200,
      "label": "Succeed",
      "message": "operation succeed",
      "data": "admin"
    }
    ```

## 8、/oauth2/refresh-token

 + 描述：刷新token

  + Http请求方式：POST

  + 数据提交方式: application/json

  + 请求参数: 

    | 参数名        | 必选 | 类型 | 说明        |
    | ------------- | ---- | ---- | ----------- |
    | refresh_token | True | str  | 刷新的token |
    | client_id     | True | str  | 应用的id    |
    
  + 请求参数示例

    ```json
    {
      ”client_id“: "sQi2cF4iXCUAKfPfacmniyeQ",
      "refresh_token": "sQi2cF4iXCUAKfPfacmniyeQsQi2cF4iXCUAKfPfacmniyeQsQi2cF4iXCUAKfPfacmniyeQsQi2cF4iXCUAKfPfacmniyeQ"
      
    }
    ```
    
  + 返回体:

    | 参数名  | 类型   | 说明                     |
    | ------- | ------ | ------------------------ |
    | code    | int    | 状态码                   |
    | label   | str    | 标签                     |
    | message | str    | 状态码对应的信息         |
    | data    | Object | 返回刷新后的access_token |

  + 返回示例:

    ```json
    {
      "code": 200,
      "label": "Succeed",
      "message": "operation succeed",
      "data": {
        	"access_token":""
      }
    }
    ```

## 9、/oauth2/register

 + 描述：应用用户的注册

  + Http请求方式：POST

  + 数据提交方式: application/json

  + 请求参数: 

    | 参数名   | 必选 | 类型 | 说明         |
    | -------- | ---- | ---- | ------------ |
    | username | True | str  | 用户名       |
    | password | True | str  | 用户安全密码 |
    | email    | True | int  | 邮箱地址     |
    
  + 请求参数示例

    ```json
    {
      ”username“: "admin",
      "password": "123456",
      "email": "register@163.com"
    }
    ```
    
  + 返回体:

    | 参数名  | 类型 | 说明             |
    | ------- | ---- | ---------------- |
    | code    | int  | 状态码           |
    | label   | str  | 标签             |
    | message | str  | 状态码对应的信息 |

  + 返回示例:

    ```json
    {
      "code": 200,
      "label": "Succeed",
      "message": "operation succeed"
    }
    ```

## 10、/oauth2/manager-login

 + 描述：认证中心后台管理用户登录

  + Http请求方式：POST

  + 数据提交方式: application/json

  + 请求参数: 

    | 参数名   | 必选 | 类型 | 说明           |
    | -------- | ---- | ---- | -------------- |
    | username | True | str  | 后台用户用户名 |
    | password | True | str  | 用户的安全密码 |
    
  + 请求参数示例

    ```json
    {
      ”username“: "admin",
      "password": "123456"
    }
    ```
    
  + 返回体:

    | 参数名  | 类型 | 说明             |
    | ------- | ---- | ---------------- |
    | code    | int  | 状态码           |
    | label   | str  | 标签             |
    | message | str  | 状态码对应的信息 |

  + 返回示例:

    ```json
    {
      "code": 200,
      "label": "Succeed",
      "message": "operation succeed",
      "data": {
        	"user_token":""
      }
    }
    ```

## 11、/oauth2/login

 + 描述：客户端用户登录

  + Http请求方式：POST

  + 数据提交方式: application/json

  + 请求参数: 

    | 参数名   | 必选 | 类型 | 说明             |
    | -------- | ---- | ---- | ---------------- |
    | username | True | str  | 客户端用户用户名 |
    | password | True | str  | 用户的安全密码   |
    
  + 请求参数示例

    ```json
    {
      ”username“: "user-1",
      "password": "123456"
      
    }
    ```
    
  + 返回体:

    | 参数名  | 类型 | 说明             |
    | ------- | ---- | ---------------- |
    | code    | int  | 状态码           |
    | label   | str  | 标签             |
    | message | str  | 状态码对应的信息 |

  + 返回示例:

    ```json
    {
      "code": 200,
      "label": "Succeed",
      "message": "operation succeed"
    }
    ```

## 12、/oauth2/logout

 + 描述：客户端用户用户退出登录
  + Http请求方式：GET
  + 数据提交方式: application/json
  + 请求参数:  **无**
  + **备注：**退出登录后，会清除认证中心内该用户的所有token信息（包括登录的cookie），同时会回调已经登录的所有应用，并清除单个应用内的局部令牌

## 13、/oauth2/login-status

 + 描述：用户鉴权登录的状态，使用场景为其他应用登录后另一个应用的无感知登录

  + Http请求方式：POST

  + 数据提交方式: application/json

  + 请求参数: 

    | 参数名    | 必选 | 类型 | 说明     |
    | --------- | ---- | ---- | -------- |
    | client_id | True | str  | 应用的id |
    
  + 请求参数示例

    ```json
    {
      ”client_id“: "sQi2cF4iXCUAKfPfacmniyeQ"
    }
    ```
    
  + 返回体:

    | 参数名  | 类型   | 说明                       |
    | ------- | ------ | -------------------------- |
    | code    | int    | 状态码                     |
    | label   | str    | 标签                       |
    | message | str    | 状态码对应的信息           |
    | data    | object | 登录后认证中心后发放的令牌 |

  + 返回示例:

    ```json
    {
      "code": 200,
      "label": "Succeed",
      "message": "operation succeed",
      "data": {
        	"access_token":"",
        	"refresh_token":""
      }
    }
    ```

    

