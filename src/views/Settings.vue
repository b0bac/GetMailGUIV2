<template>
  <div class="settings-container">
    <el-card>
      <template #header>
        <span>⚙️ 设置</span>
      </template>

      <el-tabs v-model="activeTab">
        <el-tab-pane label="账户信息" name="account">
          <el-descriptions :column="1" border>
            <el-descriptions-item label="邮箱">{{ mailStore.email }}</el-descriptions-item>
            <el-descriptions-item label="会话 ID">{{ mailStore.sessionId }}</el-descriptions-item>
          </el-descriptions>
        </el-tab-pane>

        <el-tab-pane label="关于" name="about">
          <el-descriptions :column="1" border>
            <el-descriptions-item label="版本">2.0.0</el-descriptions-item>
            <el-descriptions-item label="作者">挖洞的土拨鼠</el-descriptions-item>
            <el-descriptions-item label="GitHub">
              <a href="https://github.com/b0bac/GetMail" target="_blank">
                https://github.com/b0bac/GetMail
              </a>
            </el-descriptions-item>
          </el-descriptions>
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useMailStore } from '@/stores/mail'

const mailStore = useMailStore()
const activeTab = ref('account')
</script>

<style scoped>
.settings-container {
  padding: 20px;
}
</style>
