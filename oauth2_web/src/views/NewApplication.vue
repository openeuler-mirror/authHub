<script setup lang="ts">
import { api } from '@/api'
import {
  AllowedGrantTypes,
  AllowedResponsesTypes,
  AllowedScopeTypes,
  TokenEndpoinAuthMethod,
} from '@/api/path/types'
import { ElMessage, FormInstance, FormRules } from 'element-plus'
import { reactive, ref } from 'vue'

interface Form {
  clientName: string
  clientUri: string
  redirectUris: string
  skipAuthorization: boolean
  registerCallbackUris: string[]
  logoutCallbackUris: string[]
  allowedScope: AllowedScopeTypes[]
  grantTypes: AllowedGrantTypes[]
  responseTypes: AllowedResponsesTypes[]
  tokenEndpointAuthMethod: TokenEndpoinAuthMethod
}

withDefaults(
  defineProps<{
    visible: boolean
  }>(),
  {
    visible: false,
  },
)

const emits = defineEmits(['update:visible', 'success'])

const formRef = ref<FormInstance>()

const form = reactive<Form>({
  clientName: '',
  clientUri: '',
  redirectUris: '',
  skipAuthorization: true,
  registerCallbackUris: [],
  logoutCallbackUris: [],
  allowedScope: ['email', 'phone', 'username', 'openid', 'offline_access'],
  grantTypes: ['authorization_code'],
  responseTypes: ['code'],
  tokenEndpointAuthMethod: 'none',
})

const rules = reactive<FormRules<keyof Form>>({
  clientName: [{ required: true, message: '请输入应用名称', trigger: 'blur' }],
  clientUri: [{ required: true, message: '请输入应用地址', trigger: 'blur' }],
  redirectUris: [{ required: true, message: '请输入应用回调地址', trigger: 'blur' }],
})

const isSubmiting = ref(false)
async function generateApplication() {
  isSubmiting.value = true
  const {
    clientName,
    clientUri,
    redirectUris,
    skipAuthorization,
    registerCallbackUris,
    logoutCallbackUris,
    allowedScope,
    grantTypes,
    responseTypes,
    tokenEndpointAuthMethod,
  } = form
  const [, res] = await api.createApplication({
    client_name: clientName,
    client_uri: clientUri,
    redirect_uris: redirectUris.split(','),
    skip_authorization: skipAuthorization,
    register_callback_uris: registerCallbackUris,
    logout_callback_uris: logoutCallbackUris,
    scope: allowedScope,
    grant_types: grantTypes,
    response_types: responseTypes,
    token_endpoint_auth_method: tokenEndpointAuthMethod,
  })
  if (res) {
    ElMessage.success('Success')
    emits('success')
    emits('update:visible', false)
  }
  isSubmiting.value = false
}

async function handleSubmit() {
  if (!formRef.value) return
  await formRef.value.validate((valid) => {
    if (valid) {
      generateApplication()
    }
  })
}

function handleClose() {
  formRef.value?.resetFields()
  emits('update:visible', false)
}
</script>
<template>
  <el-dialog
    :model-value="visible"
    title="创建应用"
    destroy-on-close
    @closed="handleClose"
    width="630px"
  >
    <el-form ref="formRef" :model="form" :rules="rules" label-width="130px">
      <el-form-item label="应用名称" prop="clientName">
        <el-input v-model:model-value="form.clientName" placeholder="应用名称" />
      </el-form-item>
      <el-form-item label="应用主页" prop="clientUri">
        <el-input v-model:model-value="form.clientUri" placeholder="应用主页" />
      </el-form-item>
      <el-form-item label="应用回调地址" prop="redirectUris">
        <el-input
          v-model:model-value="form.redirectUris"
          type="textarea"
          placeholder="应用回调地址"
        />
      </el-form-item>
      <el-form-item label="用户知情同意页面" prop="shipAuthorization">
        <el-switch v-model:model-value="form.skipAuthorization" />
      </el-form-item>
    </el-form>
    <template #footer>
      <div class="dialog-footer">
        <el-button @click="emits('update:visible', false)">取消</el-button>
        <el-button :loading="isSubmiting" @click="handleSubmit" type="primary"> 创建 </el-button>
      </div>
    </template>
  </el-dialog>
</template>
<style scoped></style>
