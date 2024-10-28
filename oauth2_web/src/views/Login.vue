<script setup lang="ts">
import UserLayout from '@/layouts/UserLayout.vue'
import { ElForm, ElFormItem, ElInput, ElButton, FormRules, FormInstance } from 'element-plus'
import { reactive, ref } from 'vue'
import { User, Lock } from '@element-plus/icons-vue'
import { useRouter, useRoute } from 'vue-router'
import { api } from '@/api'

interface Form {
  username: string
  password: string
}

const route = useRoute()
const router = useRouter()

const authorizationUri = route.query.authorization_uri || ''

const formRef = ref<FormInstance>()

const form = reactive<Form>({
  username: '',
  password: '',
})

const rules = reactive<FormRules<Form>>({
  username: [{ validator: validateUsername, trigger: 'blur' }],
  password: [{ validator: validatePassword, trigger: 'blur' }],
})

/**
 * Validates a username based on a predefined regular expression.
 *
 * @param {any} _rule - The validation rule.
 * @param {any} value - The username to be validated.
 * @param {any} callback - The callback function to handle the validation result.
 * @return {void}
 */
function validateUsername(_rule: any, value: any, callback: any): void {
  const regex = /^[a-z0-9]{5,20}$/i
  if (!regex.test(value)) {
    callback(new Error('请输入5-20位字母或数字组成的用户名!'))
  }
  callback()
}

/**
 * Validates a password based on a predefined regular expression.
 *
 * @param {any} _rule - The validation rule.
 * @param {any} value - The password to be validated.
 * @param {any} callback - The callback function to handle the validation result.
 * @return {Promise<void>} A promise that resolves if the password is valid, or rejects with an error message if it's not.
 */
function validatePassword(_rule: any, value: any, callback: any): void {
  const regex = /^[a-z0-9]{6,20}$/i
  if (!regex.test(value)) {
    callback(new Error('请输入6-20位字母或数字组成的密码!'))
  }
  callback()
}

async function handleSubmit() {
  await formRef.value?.validate((valid) => {
    if (valid) {
      login()
    }
  })
}

const isSubmiting = ref(false)
async function login() {
  isSubmiting.value = true
  if (!authorizationUri) {
    const [_, res] = await api.loginManager(form)
    if (res) {
      localStorage.setItem('oauth2_token', res.user_token)
      router.push('/oauth/authorize/application')
    }
  } else {
    const [_, res] = await api.login(form)
    if (res) {
      const url = new URL(window.location.href)
      const authUrl = `${url.origin}${authorizationUri}`
      window.location.href = authUrl
    }
  }
  isSubmiting.value = false
}

function handleToRegister() {
  router.push({ path: '/oauth/authorize/register', query: route.query })
}
</script>
<template>
  <div class="user-login">
    <UserLayout>
      <el-form ref="formRef" label-width="auto" size="large" :model="form" :rules="rules">
        <el-form-item prop="username">
          <el-input v-model="form.username" placeholder="请输入您的用户名" :prefix-icon="User" />
        </el-form-item>

        <el-form-item prop="password">
          <el-input
            v-model="form.password"
            type="password"
            placeholder="请输入您的密码"
            show-password
            :prefix-icon="Lock"
          />
        </el-form-item>

        <el-form-item>
          <el-button
            :loading="isSubmiting"
            @click="handleSubmit"
            html-type="submit"
            class="submit-button"
            type="primary"
            size="large"
            >登录
          </el-button>
        </el-form-item>

        <el-form-item>
          <div class="jump-registar">
            <span>没有账号?</span>
            <span class="spin-top-jump" @click="handleToRegister"> 立即注册</span>
          </div>
        </el-form-item>
      </el-form>
    </UserLayout>
  </div>
</template>
<style lang="scss" scoped>
.user-login {
  height: 100vh;
  background: #eee;

  :deep(.el-input__wrapper) {
    border-radius: 0;
  }

  .submit-button {
    width: 100%;
    background-color: #002fa7;
    border-radius: 0;
    font-size: 16px;
  }

  .login-gitee {
    width: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;

    img {
      width: 62px;
    }

    .login-gitee-text {
      font-size: 16px;
      padding-left: 10px;
      line-height: 40px;
    }
  }

  .jump-registar {
    width: 100%;
    text-align: right;
    margin-top: -20px;

    .spin-top-jump {
      color: #005980;
      cursor: pointer;
    }
  }
}
</style>

