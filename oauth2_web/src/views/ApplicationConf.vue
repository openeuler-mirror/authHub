<script setup lang="ts">
import { Application, ApplicationReqParams } from '@/api/path/types'
import { ElMessage, FormInstance, FormRules } from 'element-plus'
import { computed, reactive, ref, watch } from 'vue'
import { CopyDocument, Hide, View } from '@element-plus/icons-vue'
import { isDeepEqual } from '@/utils'

interface Form {
  clientName: string
  clientUri: string
  redirectUris: string
  registerCallbackUris: string
  logoutCallbackUris: string
}

const props = defineProps<{
  application?: Application
}>()

const emits = defineEmits<{
  (e: 'updateApplication', application: Partial<ApplicationReqParams>): void
}>()

const formRef = ref<FormInstance>()
const isHideClientSecret = ref(true)

const form = reactive<Form>({
  clientName: '',
  clientUri: '',
  redirectUris: '',
  registerCallbackUris: '',
  logoutCallbackUris: '',
})

const originForm = reactive<Form>({
  clientName: '',
  clientUri: '',
  redirectUris: '',
  registerCallbackUris: '',
  logoutCallbackUris: '',
})

const rules = reactive<FormRules<keyof Form>>({
  clientName: [{ required: true, message: '请输入应用名称', trigger: 'blur' }],
  clientUri: [{ required: true, message: '请输入应用地址', trigger: 'blur' }],
  redirectUris: [{ required: true, message: '请输入应用回调地址', trigger: 'blur' }],
})

const clientSecret = computed(() => {
  if (!props.application) return ''
  return isHideClientSecret.value
    ? `${props.application?.client_info.client_secret.substring(0, 5)}***************`
    : `${props.application?.client_info.client_secret}`
})

function handleReset() {
  if (!formRef.value) return
  form.clientName = originForm.clientName
  form.clientUri = originForm.clientUri
  form.redirectUris = originForm.redirectUris
  form.registerCallbackUris = originForm.registerCallbackUris
  form.logoutCallbackUris = originForm.logoutCallbackUris
  ElMessage.success('Reset successfully')
}

const isSaving = ref(false)
async function handleSave() {
  if (!formRef.value) return
  isSaving.value = true
  await formRef.value.validate((valid) => {
    if (!valid) {
      ElMessage.error('表单验证失败')
      return
    }
    const isEqual = isDeepEqual(form, originForm)
    if (isEqual) {
      ElMessage.warning('未做任何修改')
      return
    }
    const application: Partial<ApplicationReqParams> = {
      client_uri: form.clientUri,
      redirect_uris: form.redirectUris.split(','),
      register_callback_uris: form.registerCallbackUris ? form.registerCallbackUris.split(',') : [],
      logout_callback_uris: form.logoutCallbackUris ? form.logoutCallbackUris.split(',') : [],
    }
    emits('updateApplication', application)
  })
  isSaving.value = false
}

function handleCopy(data: string) {
  navigator.clipboard.writeText(data)
  ElMessage.info('复制成功')
}

function initFormData() {
  form.clientName = props.application?.client_metadata.client_name || ''
  form.clientUri = props.application?.client_metadata.client_uri || ''
  form.redirectUris = props.application?.client_metadata.redirect_uris.join(',') || ''
  form.registerCallbackUris = props.application?.client_metadata.register_callback_uris.length
    ? props.application?.client_metadata.register_callback_uris.join(',')
    : ''
  form.logoutCallbackUris = props.application?.client_metadata.logout_callback_uris.length
    ? props.application?.client_metadata.logout_callback_uris.join(',')
    : ''
  originForm.clientName = form.clientName
  originForm.clientUri = form.clientUri
  originForm.redirectUris = form.redirectUris
  originForm.registerCallbackUris = form.registerCallbackUris
  originForm.logoutCallbackUris = form.logoutCallbackUris
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
  <div class="application-conf">
    <el-form ref="formRef" :model="form" :rules="rules">
      <h2>应用信息</h2>

      <el-row>
        <el-col :span="12">
          <el-form-item prop="clientName">
            <p class="form-item-title required">应用名称</p>
            <el-input v-model:model-value="form.clientName" placeholder="应用名称" disabled />
          </el-form-item>
        </el-col>
      </el-row>

      <h2>端点信息</h2>
      <el-row style="margin-bottom: 20px">
        <el-col :span="12" class="desc-row">
          <div class="desc-title">Client ID</div>
          <div class="desc-content" v-if="application?.client_info.client_id">
            <el-space class="copy-line" @click="handleCopy(application.client_info.client_id)">
              {{ application.client_info.client_id }}
              <el-tooltip class="box-item" effect="light" content="点击复制" placement="top">
                <el-icon>
                  <CopyDocument />
                </el-icon>
              </el-tooltip>
            </el-space>
          </div>
        </el-col>
        <el-col :span="12" class="desc-row">
          <div class="desc-title">Client Secret</div>
          <div class="desc-content" v-if="clientSecret">
            <el-space>
              {{ clientSecret }}
              <el-icon @click="isHideClientSecret = !isHideClientSecret" style="cursor: pointer">
                <Hide v-if="isHideClientSecret" />
                <View v-else />
              </el-icon>
            </el-space>
          </div>
        </el-col>
      </el-row>

      <h2>认证配置</h2>
      <el-row>
        <el-col :span="12">
          <el-form-item prop="clientUri">
            <p class="form-item-title required">应用地址</p>
            <el-input v-model:model-value="form.clientUri" placeholder="应用地址" />
          </el-form-item>
          <el-form-item prop="redirectUris">
            <p class="form-item-title required">登录回调URL</p>
            <el-input
              v-model:model-value="form.redirectUris"
              placeholder="多个URL用英文逗号「,」隔开"
              type="textarea"
            />
          </el-form-item>
          <el-form-item prop="registerCallbackUris">
            <p class="form-item-title">注册回调URL</p>
            <el-input
              v-model:model-value="form.registerCallbackUris"
              placeholder="多个URL用英文逗号「,」隔开"
              type="textarea"
            />
          </el-form-item>
          <el-form-item prop="logoutCallbackUris">
            <p class="form-item-title">登出回调URL</p>
            <el-input
              v-model:model-value="form.logoutCallbackUris"
              placeholder="多个URL用英文逗号「,」隔开"
              type="textarea"
            />
          </el-form-item>
        </el-col>
      </el-row>
      <el-form-item>
        <el-button :loading="isSaving" type="primary" @click="handleSave">保存</el-button>
        <el-button @click="handleReset">重置</el-button>
      </el-form-item>
    </el-form>
  </div>
</template>
<style lang="scss" scoped>
.application-conf {
  width: 80%;

  h2 {
    font-size: 20px;
    margin-bottom: 20px;
    font-weight: 500;
  }

  .form-item-title {
    font-size: 15px;
    margin-right: 10px;
    margin-bottom: 5px;
    color: #4e5969;

    .warn-icon {
      cursor: pointer;
      width: 18px;
      height: 18px;
      border-radius: 4px;
      font-size: 14px;

      &:hover {
        background: #f5f7fa;
      }
    }
  }

  .required::after {
    content: '*';
    color: red;
    margin-left: 4px;
    font-size: 16px;
    vertical-align: middle;
  }

  .desc-row {
    display: flex;
    font-size: 14px;

    .desc-title {
      width: 20%;
      color: #4e5969;
    }

    .desc-content {
      width: 80%;
      color: #4e5969;

      .copy-line {
        cursor: pointer;
      }
    }
  }
}
</style>
