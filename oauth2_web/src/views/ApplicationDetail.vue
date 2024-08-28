<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Back } from '@element-plus/icons-vue'
import { Application, ApplicationReqParams } from '@/api/path/types'
import { api } from '@/api'
import ApplicationConf from './ApplicationConf.vue'
import ProtocolConf from './ProtocolConf.vue'
import { ElMessage } from 'element-plus'

const updateForm = reactive<ApplicationReqParams>({
  client_uri: '',
  redirect_uris: [],
  register_callback_uris: [],
  logout_callback_uris: [],
  scope: [],
  grant_types: [],
  response_types: [],
  token_endpoint_auth_method: 'none',
  skip_authorization: false,
})

const route = useRoute()
const router = useRouter()

const clientId = ref(route.params.clientId as string)

const activeName = ref('applicationConf')

const application = ref<Application>()

async function getApplicationById(clientId: string) {
  const [, res] = await api.queryApplicationByClientId(clientId)
  if (res) {
    application.value = res
    updateForm.client_uri = res.client_metadata.client_uri
    updateForm.redirect_uris = res.client_metadata.redirect_uris
    updateForm.register_callback_uris = res.client_metadata.register_callback_uris
    updateForm.logout_callback_uris = res.client_metadata.logout_callback_uris
    updateForm.scope = res.client_metadata.scope
    updateForm.grant_types = res.client_metadata.grant_types
    updateForm.response_types = res.client_metadata.response_types
    updateForm.token_endpoint_auth_method = res.client_metadata.token_endpoint_auth_method
    updateForm.skip_authorization = res.client_metadata.skip_authorization
  }
}

async function handleUpdateApplication(params: Partial<ApplicationReqParams>) {
  const updateParams = { ...updateForm, ...params }

  const [_, res] = await api.updateApplication(clientId.value, updateParams)
  if (res) {
    getApplicationById(clientId.value as string)
    ElMessage.success('更新成功')
  }
}

onMounted(() => {
  if (!clientId.value) return
  getApplicationById(clientId.value as string)
})
</script>
<template>
  <div class="application-detail">
    <span class="back" @click="router.go(-1)">
      <el-space>
        <el-icon>
          <Back />
        </el-icon>
        返回
      </el-space>
    </span>

    <div class="client-header">
      <div class="client-header__image">
        <img src="@/assets/imgs/openeuler_logo.png" alt="" class="" />
      </div>
      <div class="client-header__info">
        {{ application?.client_metadata.client_name }}
      </div>
    </div>

    <el-tabs v-model="activeName" class="demo-tabs" :lazy="true">
      <el-tab-pane label="应用配置" name="applicationConf">
        <ApplicationConf :application="application" @update-application="handleUpdateApplication" />
      </el-tab-pane>
      <el-tab-pane label="协议配置" name="ProtocolConf">
        <ProtocolConf :application="application" @update-application="handleUpdateApplication" />
      </el-tab-pane>
    </el-tabs>
  </div>
</template>
<style lang="scss" scoped>
.application-detail {
  padding: 20px;

  .back {
    cursor: pointer;
    color: #959d9c;
    font-size: 14px;
    display: flex;
    align-items: center;
  }

  .client-header {
    display: flex;
    align-items: center;
    justify-content: start;
    margin-top: 15px;

    &__image {
      width: 70px;
      height: 70px;
      background: #ebf0ff;
      display: flex;
      justify-content: center;
      align-items: center;
      border-radius: 4px;

      img {
        width: 55%;
        height: 55%;
      }
    }

    &__info {
      margin-left: 20px;
      font-weight: bold;
    }
  }
}
</style>
