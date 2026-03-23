<template>
  <el-container class="inbox-container">
    <!-- 邮件列表 -->
    <el-aside width="400px" class="mail-list">
      <div class="list-header">
        <span>{{ currentFolder }}</span>
        <span class="count">{{ pagination.total }} 封</span>
      </div>
      
      <el-scrollbar class="mail-scroll">
        <div 
          v-for="mail in mails" 
          :key="mail.id"
          class="mail-item"
          :class="{ active: currentMail?.id === mail.id, unread: !mail.is_read }"
          @click="handleSelectMail(mail)"
        >
          <div class="mail-sender">{{ mail.sender }}</div>
          <div class="mail-subject">{{ mail.subject || '(无主题)' }}</div>
          <div class="mail-meta">
            <span class="mail-time">{{ formatDate(mail.received) }}</span>
            <el-icon v-if="mail.has_attachments"><Paperclip /></el-icon>
          </div>
        </div>
      </el-scrollbar>

      <!-- 分页 -->
      <div class="pagination">
        <el-pagination
          v-model:current-page="currentPage"
          :total="pagination.total"
          :page-size="pagination.pageSize"
          layout="prev, pager, next"
          small
          @current-change="handlePageChange"
        />
      </div>
    </el-aside>

    <!-- 邮件详情 -->
    <el-main class="mail-detail">
      <div v-if="currentMail" class="detail-content">
        <div class="detail-header">
          <h2>{{ currentMail.subject || '(无主题)' }}</h2>
          <div class="detail-meta">
            <div class="meta-row">
              <strong>发件人：</strong>
              <span>{{ currentMail.sender?.name }} &lt;{{ currentMail.sender?.email }}&gt;</span>
            </div>
            <div class="meta-row" v-if="currentMail.to?.length">
              <strong>收件人：</strong>
              <span>{{ currentMail.to.map(r => r.email).join(', ') }}</span>
            </div>
            <div class="meta-row" v-if="currentMail.cc?.length">
              <strong>抄送：</strong>
              <span>{{ currentMail.cc.map(r => r.email).join(', ') }}</span>
            </div>
            <div class="meta-row">
              <strong>时间：</strong>
              <span>{{ formatDateTime(currentMail.received) }}</span>
            </div>
          </div>
        </div>

        <el-divider />

        <!-- 邮件正文 -->
        <div class="detail-body" v-html="currentMail.body"></div>

        <!-- 附件 -->
        <div v-if="currentMail.attachments?.length" class="detail-attachments">
          <el-divider>附件</el-divider>
          <div class="attachment-list">
            <div 
              v-for="att in currentMail.attachments" 
              :key="att.name"
              class="attachment-item"
            >
              <el-icon><Document /></el-icon>
              <span class="att-name">{{ att.name }}</span>
              <span class="att-size">{{ formatSize(att.size) }}</span>
              <el-button 
                type="primary" 
                link 
                size="small"
                @click="handleDownload(att)"
              >
                下载
              </el-button>
            </div>
          </div>
        </div>
      </div>
      
      <el-empty v-else description="选择一封邮件查看" />
    </el-main>
  </el-container>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useMailStore } from '@/stores/mail'
import { ElMessage } from 'element-plus'
import dayjs from 'dayjs'

const mailStore = useMailStore()

const currentPage = ref(1)
const currentMail = computed(() => mailStore.currentMail)
const mails = computed(() => mailStore.mails)
const currentFolder = computed(() => mailStore.currentFolder)
const pagination = computed(() => mailStore.pagination)

onMounted(async () => {
  await mailStore.loadMails('Inbox')
})

const handleSelectMail = async (mail) => {
  await mailStore.loadMailDetail(mail.id)
}

const handlePageChange = async (page) => {
  await mailStore.loadMails(currentFolder.value, page)
}

const handleDownload = async (attachment) => {
  try {
    const result = await mailStore.downloadAttachment(currentMail.value.id, attachment.name)
    
    // 下载文件
    const link = document.createElement('a')
    link.href = `data:${attachment.type};base64,${result.data}`
    link.download = attachment.name
    link.click()
    
    ElMessage.success('下载成功')
  } catch (error) {
    ElMessage.error('下载失败')
  }
}

const formatDate = (dateStr) => {
  if (!dateStr) return ''
  const date = dayjs(dateStr)
  const now = dayjs()
  if (date.isSame(now, 'day')) {
    return date.format('HH:mm')
  } else if (date.isSame(now, 'year')) {
    return date.format('MM-DD')
  }
  return date.format('YYYY-MM-DD')
}

const formatDateTime = (dateStr) => {
  if (!dateStr) return ''
  return dayjs(dateStr).format('YYYY-MM-DD HH:mm:ss')
}

const formatSize = (bytes) => {
  if (!bytes) return ''
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
}
</script>

<style scoped>
.inbox-container {
  height: 100%;
}

.mail-list {
  background: #fff;
  border-right: 1px solid #e4e7ed;
  display: flex;
  flex-direction: column;
}

.list-header {
  padding: 15px 20px;
  border-bottom: 1px solid #e4e7ed;
  display: flex;
  justify-content: space-between;
  font-weight: 500;
}

.list-header .count {
  color: #909399;
  font-size: 13px;
}

.mail-scroll {
  flex: 1;
  overflow-y: auto;
}

.mail-item {
  padding: 15px 20px;
  border-bottom: 1px solid #f0f0f0;
  cursor: pointer;
  transition: background 0.2s;
}

.mail-item:hover {
  background: #f5f7fa;
}

.mail-item.active {
  background: #ecf5ff;
}

.mail-item.unread .mail-subject {
  font-weight: 600;
}

.mail-sender {
  font-size: 13px;
  color: #606266;
  margin-bottom: 5px;
}

.mail-subject {
  font-size: 14px;
  color: #303133;
  margin-bottom: 5px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.mail-meta {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: #909399;
}

.pagination {
  padding: 15px;
  border-top: 1px solid #e4e7ed;
  display: flex;
  justify-content: center;
}

.mail-detail {
  background: #fff;
  overflow-y: auto;
}

.detail-content {
  padding: 20px;
}

.detail-header h2 {
  margin: 0 0 15px;
  font-size: 20px;
}

.detail-meta {
  font-size: 13px;
  color: #606266;
}

.meta-row {
  margin-bottom: 8px;
}

.meta-row strong {
  color: #303133;
}

.detail-body {
  font-size: 14px;
  line-height: 1.8;
  color: #303133;
}

.attachment-list {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.attachment-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 15px;
  background: #f5f7fa;
  border-radius: 4px;
  font-size: 13px;
}

.att-name {
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.att-size {
  color: #909399;
}
</style>
