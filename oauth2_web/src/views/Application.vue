<script setup lang="ts">
import { api } from '@/api'
import { computed, onMounted, ref } from 'vue'
import { Search } from '@element-plus/icons-vue'
import ApplicationCard from '@/components/ApplicationCard.vue'
import { Application } from '@/api/path/types'
import NewApplication from './NewApplication.vue'

const applications = ref<Application[]>([])

const isLoading = ref(false)
const searchKey = ref('')

const filteredApplications = computed(() => {
  if (!searchKey.value) {
    return applications.value
  }
  return applications.value.filter((item) =>
    item.client_metadata.client_name.includes(searchKey.value),
  )
})

/**
 * Retrieves all applications and updates the applications list.
 *
 * @return {Promise<void>}
 */
async function getAllApplications(): Promise<void> {
  isLoading.value = true
  const [, res] = await api.queryAllApplications()
  if (res) {
    applications.value = res.applications
  }
  isLoading.value = false
}

const isNewDialogVisible = ref(false)
onMounted(() => {
  getAllApplications()
})
</script>
<template>
  <div class="user-center">
    <header class="user-center-header">
      <span class="user-center-header__title">自建应用</span>
      <el-button type="primary" @click="isNewDialogVisible = true">创建应用</el-button>
    </header>

    <div class="user-center-main">
      <el-input
        class="search"
        v-model:model-value="searchKey"
        placeholder="请输入关键词搜索"
        :prefix-icon="Search"
      />

      <el-row v-if="applications.length" :gutter="10" v-loading="isLoading">
        <template v-for="item in filteredApplications" :key="item.client_info.client_id">
          <el-col
            :xl="{ span: 6 }"
            :lg="{ span: 8 }"
            :md="{ span: 8 }"
            :sm="{ span: 12 }"
            :xs="{ span: 24 }"
            style="margin-top: 10px"
          >
            <ApplicationCard
              :title="item.client_metadata.client_name"
              :application="item"
              @delete-success="getAllApplications"
            />
          </el-col>
        </template>
      </el-row>
      <el-empty v-else description="无应用" />
    </div>
    <NewApplication v-model:visible="isNewDialogVisible" @success="getAllApplications" />
  </div>
</template>
<style lang="scss" scoped>
.user-center {
  padding: 20px;

  &-header {
    display: flex;
    justify-content: space-between;
    align-items: center;

    &__title {
      font-size: 22px;
      font-weight: bold;
    }
  }

  &-main {
    margin-top: 30px;
    padding: 20px 0;
    border-top: 1px solid #eee;
    display: flex;
    flex-direction: column;

    .search {
      width: 300px;
      margin-bottom: 20px;

      :deep(.el-input__wrapper) {
        background: #f7f8fa;
      }
    }
  }
}
</style>
