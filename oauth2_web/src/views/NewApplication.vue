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
  clientName: [{ validator: validateClientName, trigger: 'blur' }],
  clientUri: [{ validator: validateRedirectUris, trigger: 'blur' }],
  redirectUris: [{ validator: validateRedirectUris, trigger: 'blur' }],
})

function validateClientName(_rule: any, value: any, callback: any): void {
  const regex = /^.{5,20}$/i
  if (!regex.test(value)) {
    callback(new Error('应用名称长度必须在5-20之间!'))
  }
  callback()
}

function validateRedirectUris(_rule: any, value: any, callback: any): void {
  const regex =
    /^(((ht|f)tps?):\/\/)([^!@#$%^&*?.\s-]([^!@#$%^&*?.\s]{0,63}[^!@#$%^&*?.\s])?\.)+([a-z]{2,6})?\/?/
  console.log(regex.test(value))
  if (!regex.test(value)) {
    callback(new Error('请输入正确的url!'))
  }
  callback()
}

const isSubmitting = ref(false)
async function generateApplication() {
  isSubmitting.value = true
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
  isSubmitting.value = false
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
        <el-input v-model:model-value="form.redirectUris" placeholder="应用回调地址" />
      </el-form-item>
      <el-form-item label="用户知情同意页面" prop="shipAuthorization">
        <el-switch v-model:model-value="form.skipAuthorization" />
      </el-form-item>
    </el-form>
    <template #footer>
      <div class="dialog-footer">
        <el-button @click="emits('update:visible', false)">取消</el-button>
        <el-button :loading="isSubmitting" @click="handleSubmit" type="primary"> 创建 </el-button>
      </div>
    </template>
  </el-dialog>
</template>
<style scoped></style>

