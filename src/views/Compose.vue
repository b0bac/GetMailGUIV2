<template>
  <div class="compose-container">
    <el-card>
      <template #header>
        <span>✉️ 写邮件</span>
      </template>

      <el-form :model="form" :rules="rules" ref="formRef" label-width="80px">
        <el-form-item label="收件人" prop="to">
          <el-select
            v-model="form.to"
            multiple
            filterable
            allow-create
            default-first-option
            placeholder="输入邮箱地址"
            style="width: 100%"
          />
        </el-form-item>

        <el-form-item label="抄送">
          <el-select
            v-model="form.cc"
            multiple
            filterable
            allow-create
            default-first-option
            placeholder="输入邮箱地址"
            style="width: 100%"
          />
        </el-form-item>

        <el-form-item label="密送">
          <el-select
            v-model="form.bcc"
            multiple
            filterable
            allow-create
            default-first-option
            placeholder="输入邮箱地址"
            style="width: 100%"
          />
        </el-form-item>

        <el-form-item label="主题" prop="subject">
          <el-input v-model="form.subject" placeholder="邮件主题" />
        </el-form-item>

        <el-form-item label="正文">
          <el-input
            v-model="form.body"
            type="textarea"
            :rows="15"
            placeholder="邮件正文..."
          />
        </el-form-item>

        <el-form-item label="附件">
          <div class="attachment-area">
            <el-button @click="handleSelectFiles">
              <el-icon><Upload /></el-icon>
              选择文件
            </el-button>
            <div v-if="form.attachments.length" class="attachment-list">
              <el-tag
                v-for="(file, index) in form.attachments"
                :key="index"
                closable
                @close="handleRemoveAttachment(index)"
              >
                {{ file.split('/').pop() }}
              </el-tag>
            </div>
          </div>
        </el-form-item>

        <el-form-item>
          <el-button type="primary" :loading="loading" @click="handleSend">
            <el-icon><Promotion /></el-icon>
            发送
          </el-button>
          <el-button @click="$router.back()">取消</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useMailStore } from '@/stores/mail'
import { ElMessage } from 'element-plus'

const router = useRouter()
const mailStore = useMailStore()

const formRef = ref(null)
const loading = ref(false)

const form = reactive({
  to: [],
  cc: [],
  bcc: [],
  subject: '',
  body: '',
  attachments: []
})

const rules = {
  to: [{ required: true, message: '请输入收件人', trigger: 'change' }],
  subject: [{ required: true, message: '请输入主题', trigger: 'blur' }]
}

const handleSelectFiles = async () => {
  // Electron 环境使用原生对话框
  if (window.electronAPI) {
    const files = await window.electronAPI.dialog.selectFile()
    if (files && files.length) {
      form.attachments.push(...files)
    }
  } else {
    ElMessage.warning('请在 Electron 环境中使用文件选择功能')
  }
}

const handleRemoveAttachment = (index) => {
  form.attachments.splice(index, 1)
}

const handleSend = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    
    loading.value = true
    try {
      await mailStore.sendMail({
        to: form.to,
        cc: form.cc,
        bcc: form.bcc,
        subject: form.subject,
        body: form.body,
        attachments: form.attachments
      })
      
      ElMessage.success('邮件发送成功')
      router.push('/inbox')
    } catch (error) {
      console.error(error)
    } finally {
      loading.value = false
    }
  })
}
</script>

<style scoped>
.compose-container {
  padding: 20px;
  height: 100%;
  overflow-y: auto;
}

.attachment-area {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.attachment-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}
</style>
