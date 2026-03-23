<template>
  <div class="login-container">
    <el-card class="login-card">
      <template #header>
        <div class="login-header">
          <h1>📬 GetMail v2</h1>
          <p>Exchange 邮件读取与发送工具</p>
        </div>
      </template>

      <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
        <el-form-item label="登录账户" prop="username">
          <el-input v-model="form.username" placeholder="DOMAIN\username" />
        </el-form-item>
        
        <el-form-item label="登录凭据" prop="credential">
          <el-input 
            v-model="form.credential" 
            type="password" 
            show-password 
            placeholder="密码或 NTLM Hash (lm:nt)"
          />
        </el-form-item>
        
        <el-form-item label="邮件地址" prop="email">
          <el-input v-model="form.email" placeholder="user@domain.com" />
        </el-form-item>

        <el-divider content-position="left">高级选项</el-divider>

        <div class="autodiscover-wrapper">
          <span class="autodiscover-label">自动发现</span>
          <el-radio-group v-model="form.useAutodiscover">
            <el-radio :value="true">开启</el-radio>
            <el-radio :value="false">关闭</el-radio>
          </el-radio-group>
        </div>
        
        <el-form-item v-if="!form.useAutodiscover" label="服务器地址">
          <el-input v-model="form.server" placeholder="mail.domain.com" />
        </el-form-item>

        <el-form-item v-if="!form.useAutodiscover" label="EWS 地址">
          <el-input v-model="form.ewsUrl" placeholder="https://mail.domain.com/EWS/Exchange.asmx" />
        </el-form-item>

        <div class="login-button-wrapper">
          <el-button 
            type="primary" 
            :loading="loading" 
            @click="handleLogin"
            size="large"
          >
            登录
          </el-button>
        </div>
      </el-form>

      <div class="login-footer">
        <p>by 挖洞的土拨鼠 🦫</p>
      </div>
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
  username: '',
  credential: '',
  email: '',
  useAutodiscover: true,
  server: '',
  ewsUrl: ''
})

const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  credential: [{ required: true, message: '请输入凭据', trigger: 'blur' }],
  email: [{ required: true, message: '请输入邮件地址', trigger: 'blur' }]
}

const handleLogin = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    
    loading.value = true
    try {
      await mailStore.login({
        username: form.username,
        credential: form.credential,
        email: form.email,
        server: form.server || null,
        ews_url: form.ewsUrl || null,
        use_autodiscover: form.useAutodiscover
      })
      
      ElMessage.success('登录成功')
      router.push('/')
    } catch (error) {
      console.error(error)
    } finally {
      loading.value = false
    }
  })
}
</script>

<style scoped>
.login-container {
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.login-card {
  width: 450px;
}

.login-header {
  text-align: center;
}

.login-header h1 {
  margin: 0 0 10px;
  font-size: 28px;
}

.login-header p {
  margin: 0;
  color: #909399;
}

.login-footer {
  text-align: center;
  margin-top: 20px;
  color: #909399;
  font-size: 12px;
}

.login-button-wrapper {
  text-align: center;
  margin-top: 30px;
}

.login-button-wrapper .el-button {
  width: 100%;
  max-width: 320px;
}

.autodiscover-wrapper {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 15px;
  margin: 15px 0 20px;
}

.autodiscover-label {
  font-size: 14px;
  color: #606266;
}
</style>
