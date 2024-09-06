<script setup lang='ts'>
import { ref } from 'vue';
import { DocumentCopy, MoreFilled } from '@element-plus/icons-vue'
import { DropdownInstance, ElMessage } from 'element-plus';
import { api } from '@/api';
import { useRouter } from 'vue-router'
import { Application } from '@/api/path/types';

const props = withDefaults(defineProps<{
  title: string
  application: Application
  desc?: string
}>(), {
  desc: ''
})

const emits = defineEmits(['deleteSuccess'])

const router = useRouter()

const dropdownRef = ref<DropdownInstance>()

const isOperationVisible = ref(false)
const isDropDownVisible = ref(false)

function handleMouseLeave() {
  if (isDropDownVisible.value) {
    return
  }
  isOperationVisible.value = false
}

function handleVisible(visible: boolean) {
  if (visible) {
    isDropDownVisible.value = true
  } else {
    isDropDownVisible.value = false
  }
}

async function deleteApplication() {
  const clientId = props.application.client_info.client_id
  const [_,] = await api.deleteApplication(clientId)
  if (!_) {
    ElMessage.success('Delete Successfully')
    isDropDownVisible.value = false
    emits('deleteSuccess')
  }
}

function handleCardClick() {
  const clientId = props.application.client_info.client_id
  router.push({ name: 'applicationDetail', params: { clientId } })
}

function handleOperationClick() {
  if (!dropdownRef.value) return
  if (isDropDownVisible.value) {
    dropdownRef.value.handleClose()
  } else {
    dropdownRef.value.handleOpen()
  }
}

function handleCopy(data: string) {
  navigator.clipboard.writeText(data)
  ElMessage.info(
    '复制成功',
  )
}

</script>

<template>
  <div class="application-card" @mouseenter="isOperationVisible = true" @click="handleCardClick"
    @mouseleave="handleMouseLeave">
    <el-dropdown ref="dropdownRef" placement="bottom-end" v-show="isOperationVisible" class="operation"
      trigger="contextmenu" @visible-change="handleVisible">
      <el-icon @click.stop="handleOperationClick">
        <MoreFilled />
      </el-icon>
      <template #dropdown>
        <el-dropdown-menu>
          <el-button text type="danger" plain @click="deleteApplication">删除</el-button>
        </el-dropdown-menu>
      </template>
    </el-dropdown>
    <header class="application-card__header">
      <span class="title">{{ title }}</span>
      <span class="desc">{{ desc }}</span>
    </header>

    <div class="client-info" @click.stop="handleCopy(application.client_info.client_id)">
      <div>
        <h4>Client_Id: </h4>
        <div>
          <el-space>
            {{ application.client_info.client_id }}
            <el-icon v-show="isOperationVisible">
              <DocumentCopy />
            </el-icon>
          </el-space>
        </div>
      </div>
    </div>
  </div>
</template>
<style lang="scss" scoped>
.application-card {
  background: #F7F8FA;
  height: 180px;
  border-radius: 4px;
  padding: 20px;
  cursor: pointer;
  transition: box-shadow 0.6s ease;
  position: relative;
  display: flex;
  flex-direction: column;
  justify-content: space-between;

  .operation {
    position: absolute;
    right: 10px;
    top: 10px;
    font-size: 18px;
    width: 25px;
    height: 25px;
    display: flex;
    justify-content: center;
    align-items: center;
    border-radius: 4px;
    user-select: none;

    .delete-application {
      color: red;
    }

    &:hover {
      background: #e9eeee;
    }
  }

  &__header {
    display: flex;
    flex-direction: column;

    .title {
      font-size: 22px;
    }

    .desc {
      font-size: 12px;
      color: #959D9C;
    }
  }

  &:hover {
    box-shadow: 0 4px 20px rgba(91, 115, 139, .18), 0 0 2px rgba(91, 115, 139, .16)
  }

  .client-info {
    font-size: 14px;
    color: #909695;

    h4 {
      margin-bottom: 5px;
    }
  }
}
</style>
