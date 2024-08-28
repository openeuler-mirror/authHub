<script setup lang="ts">
import { reactive, ref, watch } from 'vue'
import {
  AllowedGrantTypes,
  AllowedResponsesTypes,
  AllowedScopeTypes,
  Application,
  ApplicationReqParams,
  TokenEndpoinAuthMethod,
} from '@/api/path/types'
import { ElMessage, FormInstance } from 'element-plus'
import { isDeepEqual } from '@/utils'
import { QuestionFilled, WarningFilled } from '@element-plus/icons-vue'

interface Form {
  skipAuthorization: boolean
  allowedScope: AllowedScopeTypes[]
  grantTypes: AllowedGrantTypes[]
  responseTypes: AllowedResponsesTypes[]
  tokenEndpointAuthMethod: TokenEndpoinAuthMethod
}

const props = defineProps<{
  application?: Application
}>()

const emits = defineEmits<{
  (e: 'updateApplication', application: Partial<ApplicationReqParams>): void
}>()

const grantOptions = ['authorization_code', 'client_credentials']
const responseTypeOptions = ['code', 'token']
const authMethodOptions = ['client_secret_basic', 'client_secret_post', 'none']
const scopeOptions = [
  {
    key: 'openid',
    value: 'openid',
    disabled: true,
  },
  {
    key: 'username',
    value: 'username',
    disabled: false,
  },
  {
    key: 'email',
    value: 'email',
    disabled: false,
  },
  {
    key: 'phone',
    value: 'phone',
    disabled: false,
  },
  {
    key: 'offline_access',
    value: 'offline_access',
    disabled: true,
  },
]

const isSaving = ref(false)

const form = reactive<Form>({
  skipAuthorization: false,
  allowedScope: [],
  grantTypes: [],
  responseTypes: [],
  tokenEndpointAuthMethod: 'none',
})

const originForm = reactive<Form>({
  skipAuthorization: false,
  allowedScope: [],
  grantTypes: [],
  responseTypes: [],
  tokenEndpointAuthMethod: 'none',
})
const formRef = ref<FormInstance>()

const protocolType = ref('OIDC')
const protocolTypeOptions = [
  {
    key: 'OIDC',
    value: 'OIDC',
    disabled: false,
  },
  {
    key: 'OAuth2',
    value: 'OAuth2',
    disabled: true,
  },
  {
    key: 'SAML2',
    value: 'SAML2',
    disabled: true,
  },
  {
    key: 'CAS',
    value: 'CAS',
    disabled: true,
  },
]
function initFormData() {
  form.grantTypes = props.application?.client_metadata.grant_types || []
  form.responseTypes = props.application?.client_metadata.response_types || []
  form.allowedScope = props.application?.client_metadata.scope || []
  form.tokenEndpointAuthMethod =
    props.application?.client_metadata.token_endpoint_auth_method || 'none'
  form.skipAuthorization = props.application?.client_metadata.skip_authorization || false

  originForm.grantTypes = form.grantTypes
  originForm.responseTypes = form.responseTypes
  originForm.allowedScope = form.allowedScope
  originForm.tokenEndpointAuthMethod = form.tokenEndpointAuthMethod
  originForm.skipAuthorization = form.skipAuthorization
}

async function handleSubmit() {
  isSaving.value = true
  const isEqual = isDeepEqual(form, originForm)
  if (isEqual) {
    ElMessage.warning('未做任何修改')
    isSaving.value = false

    return
  }

  const application: Partial<ApplicationReqParams> = {
    grant_types: form.grantTypes,
    response_types: form.responseTypes,
    scope: form.allowedScope,
    token_endpoint_auth_method: form.tokenEndpointAuthMethod,
    skip_authorization: form.skipAuthorization,
  }

  emits('updateApplication', application)
  isSaving.value = false
}

function handleReset() {
  form.grantTypes = originForm.grantTypes
  form.responseTypes = originForm.responseTypes
  form.allowedScope = originForm.allowedScope
  form.tokenEndpointAuthMethod = originForm.tokenEndpointAuthMethod
  form.skipAuthorization = originForm.skipAuthorization
}

watch(
  () => props.application,
  () => {
    initFormData()
    isSaving.value = false
  },
)
</script>
<template>
  <div class="protocol-conf">
    <el-form ref="formRef" :model="form">
      <h3>
        默认协议类型
        <el-tooltip placement="right">
          <el-icon>
            <QuestionFilled color="#DCDFE6" />
          </el-icon>
          <template #content>
            <div style="width: 180px">
              当直接访问认证地址时默认使用的协议。禁用的协议需要在下方「授权配置」中开启并保存后方可启用。
            </div>
          </template>
        </el-tooltip>
      </h3>
      <el-form-item>
        <el-radio-group v-model="protocolType">
          <el-radio
            v-for="item in protocolTypeOptions"
            :key="item.key"
            :disabled="item.disabled"
            :value="item.value"
            size="large"
            >{{ item.value }}</el-radio
          >
        </el-radio-group>
      </el-form-item>
      <h3>授权配置</h3>
      <div class="protocol-tips">
        <el-icon>
          <WarningFilled color="#DCDFE6" />
        </el-icon>
        当你使用 Authing 的身份认证功能时，默认使用 OIDC（OpenID Connect）协议进行认证。
      </div>
      <h4>授权模式</h4>
      <el-form-item prop="grantTypes">
        <el-checkbox-group v-model="form.grantTypes">
          <el-checkbox
            v-for="item in grantOptions"
            :key="item"
            :label="item"
            :value="item"
            size="large"
          />
        </el-checkbox-group>
      </el-form-item>
      <h4>返回类型</h4>
      <el-form-item prop="responseTypes">
        <el-checkbox-group v-model="form.responseTypes">
          <el-checkbox
            v-for="item in responseTypeOptions"
            :key="item"
            :label="item"
            :value="item"
            size="large"
          />
        </el-checkbox-group>
      </el-form-item>
      <h4>配置Scope</h4>
      <el-form-item prop="allowedScope">
        <el-checkbox-group v-model="form.allowedScope">
          <el-checkbox
            v-for="item in scopeOptions"
            :key="item.key"
            :label="item.value"
            :disabled="item.disabled"
            :value="item.value"
            size="large"
          />
        </el-checkbox-group>
      </el-form-item>
      <!-- <h4>token 身份验证方式</h4>
      <el-form-item prop="tokenEndpointAuthMethod">
        <el-radio-group v-model="form.tokenEndpointAuthMethod">
          <el-radio v-for="item in authMethodOptions" :value="item" size="large">{{
            item
          }}</el-radio>
        </el-radio-group>
      </el-form-item> -->
      <el-form-item prop="skipAuthorization" label="用户知情同意页面">
        <el-switch v-model="form.skipAuthorization" />
      </el-form-item>

      <el-form-item>
        <el-button :loading="isSaving" type="primary" @click="handleSubmit">保存</el-button>
        <el-button @click="handleReset">重置</el-button>
      </el-form-item>
    </el-form>
  </div>
</template>
<style lang="scss" scoped>
:deep(.el-checkbox > .el-checkbox__label) {
  color: #000;
}

:deep(.el-radio > .el-radio__label) {
  color: #000;
}

.protocol-conf {
  h3 {
    font-size: 16px;
    font-weight: 500;
    margin-bottom: 20px;
    display: flex;
    align-items: center;
    gap: 6px;
  }

  h4 {
    font-size: 14px;
    margin-bottom: 20px;
    font-weight: 500;
    color: #4e5969;
  }

  .protocol-tips {
    font-size: 14px;
    background: #f7f8fa;
    padding: 15px;
    margin-bottom: 15px;
    display: flex;
    align-items: center;
    gap: 6px;
  }
}
</style>
