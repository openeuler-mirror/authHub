<script setup lang="ts">
import UserLayout from '@/layouts/UserLayout.vue'
import {
  ElForm,
  ElFormItem,
  ElInput,
  ElButton,
  FormRules,
  FormInstance,
  ElMessage,
} from 'element-plus'
import { reactive, ref } from 'vue'
import { User, Lock, Message } from '@element-plus/icons-vue'
import { useRouter, useRoute } from 'vue-router'
import { api } from '@/api'

interface Form {
  username: string
  password: string
  confirmPassword: string
  email: string
}

const router = useRouter()
const route = useRoute()
const formRef = ref<FormInstance>()

const form = reactive<Form>({
  username: '',
  password: '',
  confirmPassword: '',
  email: '',
})

const rules = reactive<FormRules<Form>>({
  username: [{ validator: validateUsername, trigger: 'blur' }],
  password: [{ validator: validatePassword, trigger: 'blur' }],
  confirmPassword: [{ validator: validateConfirmPassword, trigger: 'blur' }],
  email: [{ validator: validateEmail, trigger: 'blur' }],
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

/**
 * Validates a confirm password based on a predefined regular expression and checks if it matches the original password.
 *
 * @param {any} _rule - The validation rule.
 * @param {any} value - The confirm password to be validated.
 * @param {any} callback - The callback function to handle the validation result.
 * @return {void}
 */
function validateConfirmPassword(_rule: any, value: any, callback: any): void {
  const regex = /^[a-z0-9]{6,20}$/i
  if (!regex.test(value)) {
    callback(new Error('请输入6-20位字母或数字组成的密码!'))
  } else if (value && value !== form.password) {
    callback(new Error('请确保前后两次输入的密码保持一致！'))
  }
  callback()
}

/**
 * Validates an email address based on a predefined regular expression.
 *
 * @param {any} _rule - The validation rule.
 * @param {any} value - The email address to be validated.
 * @param {any} callback - The callback function to handle the validation result.
 * @return {void}
 */
function validateEmail(_rule: any, value: any, callback: any): void {
  const regex = /^[\w.%+-]+@[a-z0-9.-]+\.[a-z]{2,}$/i
  if (!regex.test(value)) {
    callback(new Error('请输入正确的邮箱格式!'))
  }
  callback()
}

function handleToLogin() {
  router.push({ path: '/oauth/authorize/login', query: route.query })
}

async function handleSubmit() {
  await formRef.value?.validate((valid) => {
    if (valid) {
      register()
    }
  })
}

const isSubmiting = ref(false)
async function register() {
  isSubmiting.value = true
  const [_] = await api.register({
    username: form.username,
    password: form.password,
    email: form.email,
  })
  if (!_) {
    ElMessage.success('Register Successfully')
    handleToLogin()
  }
  isSubmiting.value = false
}
</script>
<template>
  <div class="user-login">
    <UserLayout>
      <el-form ref="formRef" label-width="auto" size="large" :model="form" :rules="rules">
        <el-form-item prop="username">
          <el-input
            v-model="form.username"
            placeholder="用户名5-20位,包含字母或数字"
            :prefix-icon="User"
          />
        </el-form-item>

        <el-form-item prop="password">
          <el-input
            v-model="form.password"
            type="password"
            placeholder="密码长度6-20位,包含字母或数字"
            show-password
            :prefix-icon="Lock"
          />
        </el-form-item>

        <el-form-item prop="confirmPassword">
          <el-input
            v-model="form.confirmPassword"
            type="password"
            placeholder="确认前后两次输入的密码保持一致	"
            show-password
            :prefix-icon="Lock"
          />
        </el-form-item>

        <el-form-item prop="email">
          <el-input
            v-model="form.email"
            placeholder="输入邮箱地址: 例如:xxxx@163.com"
            :prefix-icon="Message"
          />
        </el-form-item>

        <el-form-item>
          <el-button
            :loading="isSubmiting"
            @click="handleSubmit"
            class="submit-button"
            type="primary"
            size="large"
            >注册
          </el-button>
        </el-form-item>

        <el-form-item>
          <div class="jump-login">
            <span>已有账号?</span>
            <span class="spin-top-jump" @click="handleToLogin"> 返回登录</span>
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

  .jump-login {
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
