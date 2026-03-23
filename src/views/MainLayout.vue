<template>
  <el-container class="main-layout">
    <!-- 侧边栏 -->
    <el-aside width="220px" class="sidebar">
      <div class="logo">
        <h1>📬 GetMail</h1>
        <span class="version">v2.0</span>
      </div>
      
      <!-- 文件夹列表 -->
      <div class="folder-section">
        <div class="section-title">文件夹</div>
        <el-menu
          :default-active="currentFolder"
          class="folder-menu"
          @select="handleFolderSelect"
        >
          <el-menu-item 
            v-for="folder in folders" 
            :key="folder.name" 
            :index="folder.name"
          >
            <el-icon><Folder /></el-icon>
            <span>{{ folder.name }}</span>
            <el-badge 
              v-if="folder.unread_count > 0" 
              :value="folder.unread_count" 
              class="folder-badge"
            />
          </el-menu-item>
        </el-menu>
      </div>

      <!-- 底部操作 -->
      <div class="sidebar-footer">
        <el-button type="primary" @click="$router.push('/compose')">
          <el-icon><Edit /></el-icon>
          写邮件
        </el-button>
        <el-button @click="handleLogout">
          <el-icon><SwitchButton /></el-icon>
          退出
        </el-button>
      </div>
    </el-aside>

    <!-- 主体 -->
    <el-container>
      <!-- 头部 -->
      <el-header class="header">
        <div class="header-left">
          <span class="email">{{ mailStore.email }}</span>
        </div>
        <div class="header-right">
          <el-input
            v-model="searchKeyword"
            placeholder="搜索邮件"
            style="width: 300px"
            @keyup.enter="handleSearch"
          >
            <template #append>
              <el-button @click="handleSearch">
                <el-icon><Search /></el-icon>
              </el-button>
            </template>
          </el-input>
          <el-button @click="$router.push('/settings')">
            <el-icon><Setting /></el-icon>
          </el-button>
        </div>
      </el-header>

      <!-- 内容 -->
      <el-main class="main-content">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useMailStore } from '@/stores/mail'

const router = useRouter()
const mailStore = useMailStore()

const searchKeyword = ref('')

const currentFolder = computed(() => mailStore.currentFolder)
const folders = computed(() => mailStore.folders)

onMounted(async () => {
  await mailStore.loadFolders()
})

const handleFolderSelect = async (folder) => {
  await mailStore.loadMails(folder)
}

const handleSearch = async () => {
  await mailStore.loadMails(currentFolder.value, 1, searchKeyword.value)
}

const handleLogout = async () => {
  await mailStore.logout()
  router.push('/login')
}
</script>

<style scoped>
.main-layout {
  height: 100vh;
}

.sidebar {
  background-color: #1a1a2e;
  color: #fff;
  display: flex;
  flex-direction: column;
}

.logo {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #16213e;
}

.logo h1 {
  font-size: 18px;
  margin: 0;
}

.logo .version {
  font-size: 12px;
  margin-left: 8px;
  color: #909399;
}

.folder-section {
  flex: 1;
  overflow-y: auto;
}

.section-title {
  padding: 15px 20px 10px;
  font-size: 12px;
  color: #909399;
}

.folder-menu {
  border: none;
  background-color: transparent;
}

.folder-menu .el-menu-item {
  color: #fff;
}

.folder-menu .el-menu-item:hover,
.folder-menu .el-menu-item.is-active {
  background-color: #0f3460;
}

.folder-badge {
  margin-left: auto;
}

.sidebar-footer {
  padding: 15px;
  border-top: 1px solid #16213e;
}

.sidebar-footer .el-button {
  width: 100%;
  margin-bottom: 10px;
}

.header {
  background-color: #fff;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.08);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
}

.header-left .email {
  font-weight: 500;
}

.header-right {
  display: flex;
  gap: 10px;
}

.main-content {
  background-color: #f5f7fa;
  padding: 0;
  overflow: hidden;
}
</style>
