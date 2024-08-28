// Copyright (c) Huawei Technologies Co., Ltd. 2023-2024. All rights reserved.
// licensed under the Mulan PSL v2.
// You can use this software according to the terms and conditions of the Mulan PSL v2.
// You may obtain a copy of Mulan PSL v2 at:
//      http://license.coscl.org.cn/MulanPSL2
// THIS SOFTWARE IS PROVIDED ON AN 'AS IS' BASIS, WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR
// IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT, MERCHANTABILITY OR FIT FOR A PARTICULAR
// PURPOSE.
// See the Mulan PSL v2 for more details.
import type {
  AxiosError,
  AxiosRequestConfig,
  AxiosResponse,
  InternalAxiosRequestConfig,
} from 'axios'
import axios from 'axios'
import { ElMessage, ElNotification } from 'element-plus'


export interface Result<T = any> {
  code: number
  data: T
  message?: string
  label?: string
}

export interface IAnyObj {
  [index: string]: unknown
}



const request = axios.create({
  timeout: 60 * 1000,
})


request.interceptors.request.use(
  (
    config: InternalAxiosRequestConfig<any>,
  ): InternalAxiosRequestConfig<any> | Promise<InternalAxiosRequestConfig<any>> => {
    config.headers['Content-Type'] = 'application/json; charset=UTF-8'
    config.headers['Authorization'] = `${localStorage.getItem('oauth2_token')}`
    return config
  },
  (error: AxiosError) => {
    ElMessage.error(error.message)
    return Promise.reject(error)
  },
)


request.interceptors.response.use(
  async (response: AxiosResponse<any, any>): Promise<any> => {
    const { code, data } = response.data

    if (!code.toString().match(/^2\d{2}$/)) {
      switch (Number(code)) {
        case 1201:
          ElNotification.error({
            title: '用户鉴权失败',
            message: response.data.message,
          })
          setTimeout(() => {
            window.location.href = '/oauth/authorize/login'
          }, 1000)
          break
        default:
          ElNotification.success({
            title: response.data.label,
            message: response.data.message,
          })
      }
      return Promise.reject(response)
    }
    return data
  },
  (error: AxiosError) => {
    const message = error.message || 'Network Error'
    ElMessage.error(message)
    return Promise.reject(error)
  },
)

export const http = {
  get: async <T>(url: string, params?: AxiosRequestConfig): Promise<[any, T | undefined]> => {
    try {
      const result = await request.get(url, params)
      return [null, result as T]
    }
    catch (error) {
      return [error, undefined]
    }
  },

  post: async <T>(
    url: string,
    data?: object,
    params?: AxiosRequestConfig,
  ): Promise<[any, T | undefined]> => {
    try {
      const result = await request.post(url, data, params)
      return [null, result as T]
    }
    catch (error) {
      return [error, undefined]
    }
  },

  put: async <T>(url: string, data?: object, params?: object): Promise<[any, T | undefined]> => {
    try {
      const result = await request.put(url, data, { params })
      return [null, result as T]
    }
    catch (error) {
      return [error, undefined]
    }
  },

  delete: async <T>(url: string, data?: object, params?: object): Promise<[any, T | undefined]> => {
    try {
      const result = await request.delete(url, { data, params })
      return [null, result as T]
    }
    catch (error) {
      return [error, undefined]
    }
  },
}
