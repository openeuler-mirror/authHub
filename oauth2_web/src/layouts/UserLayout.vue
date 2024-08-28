<script setup lang="ts">
import { ElRow, ElCol } from 'element-plus'
</script>
<template>
  <el-row class="user-layout-wrapper">
    <el-col class="left-side" :md="{ span: 24 }" :lg="{ span: 12 }" :xl="{ span: 12 }">
      <img src="@/assets/imgs/loginPage.png" alt="loginPage" />
    </el-col>
    <el-col class="right-side" :sm="{ span: 24 }" :lg="{ span: 12 }" :xl="{ span: 12 }">
      <header class="header">
        <a href="/">
          <div class="logo">
            <img src="@/assets/imgs/openeuler_logo.png" class="openeuler-logo" alt="logo" />
            <img src="@/assets/imgs/openeuler.png" class="openeuler" alt="logo" />
          </div>
        </a>
      </header>
      <div class="main">
        <slot></slot>
      </div>
    </el-col>
  </el-row>
</template>
<style lang="scss" scoped>
.user-layout-wrapper {
  height: 100%;
}
.left-side {
  height: 100%;
  img {
    width: 500px;
    display: block;
    position: relative;
    margin: auto;
    top: 50vh;
    margin-top: -150px;
  }
}

.right-side {
  height: 100%;
  background-color: #ffffff;
  padding-top: 16vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  .header {
    .logo {
      display: flex;
      flex-direction: column;
      align-items: center;
      .openeuler-logo {
        height: 50px;
      }
      .openeuler {
        height: 30px;
        filter: var(--openeuler-logo-filter);
      }
    }
  }

  .main {
    width: 400px;
    margin: 0 auto;
    margin-top: 100px;
  }
}
</style>

