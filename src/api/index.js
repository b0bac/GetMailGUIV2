import axios from 'axios'
import { ElMessage } from 'element-plus'

// API 基础地址
const API_BASE = 'http://127.0.0.1:8001'

const api = axios.create({
  baseURL: API_BASE,
  timeout: 30000
})

// 响应拦截
api.interceptors.response.use(
  response => response.data,
  error => {
    const msg = error.response?.data?.detail || error.message || '请求失败'
    ElMessage.error(msg)
    return Promise.reject(error)
  }
)

// ==================== 邮件 API ====================

export const mailApi = {
  // 登录
  login: (data) => api.post('/api/login', data),
  
  // 登出
  logout: (sessionId) => api.post('/api/logout', null, { params: { session_id: sessionId } }),
  
  // 获取文件夹列表
  getFolders: (sessionId) => api.post('/api/folders', { session_id: sessionId }),
  
  // 获取邮件列表
  getMails: (data) => api.post('/api/mails', data),
  
  // 获取邮件详情
  getMailDetail: (sessionId, mailId) => api.post('/api/mail/detail', { 
    session_id: sessionId, 
    mail_id: mailId 
  }),
  
  // 下载附件
  downloadAttachment: (sessionId, mailId, attachmentName) => 
    api.post('/api/attachment/download', {
      session_id: sessionId,
      mail_id: mailId,
      attachment_name: attachmentName
    }),
  
  // 发送邮件
  sendMail: (data) => api.post('/api/mail/send', data)
}

export default api
