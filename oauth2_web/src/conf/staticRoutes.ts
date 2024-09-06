// Copyright (c) Huawei Technologies Co., Ltd. 2023-2024. All rights reserved.
// licensed under the Mulan PSL v2.
// You can use this software according to the terms and conditions of the Mulan PSL v2.
// You may obtain a copy of Mulan PSL v2 at:
//      http://license.coscl.org.cn/MulanPSL2
// THIS SOFTWARE IS PROVIDED ON AN 'AS IS' BASIS, WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR
// IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT, MERCHANTABILITY OR FIT FOR A PARTICULAR
// PURPOSE.
// See the Mulan PSL v2 for more details.
import type { RouteRecordRaw } from 'vue-router'

const routes: Array<RouteRecordRaw> = [
  {
    path: '/',
    redirect: '/oauth',
    children: [
      {
        path: '/oauth',
        name: 'oauth',
        redirect: '/oauth/authorize/application',
        children: [
          {
            path: '/oauth/authorize/application',
            name: 'application',
            component: () => import('@/views/Application.vue'),
          },
          {
            path: '/oauth/authorize/application/:clientId',
            name: 'applicationDetail',
            component: () => import('@/views/ApplicationDetail.vue'),
          },
          {
            path: '/oauth/authorize/login',
            name: 'login',
            component: () => import('@/views/Login.vue'),
          },
          {
            path: '/oauth/authorize/register',
            name: 'register',
            component: () => import('@/views/Register.vue'),
          },
          {
            path: '/oauth/authorize/error',
            component: () => import('@/views/Error.vue'),
            meta: {
              hidden: true,
            },
          },
        ]
      },
    ],
  }
]

export default routes
