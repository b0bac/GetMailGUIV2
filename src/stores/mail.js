import { defineStore } from 'pinia'
import { mailApi } from '@/api/index'

export const useMailStore = defineStore('mail', {
  state: () => ({
    sessionId: localStorage.getItem('session_id') || null,
    email: localStorage.getItem('email') || null,
    folders: [],
    currentFolder: 'Inbox',
    mails: [],
    currentMail: null,
    loading: false,
    pagination: {
      page: 1,
      pageSize: 20,
      total: 0
    }
  }),

  getters: {
    isLoggedIn: (state) => !!state.sessionId
  },

  actions: {
    async login(data) {
      this.loading = true
      try {
        const result = await mailApi.login(data)
        this.sessionId = result.session_id
        this.email = result.email
        localStorage.setItem('session_id', result.session_id)
        localStorage.setItem('email', result.email)
        return result
      } finally {
        this.loading = false
      }
    },

    async logout() {
      if (this.sessionId) {
        await mailApi.logout(this.sessionId)
      }
      this.sessionId = null
      this.email = null
      this.folders = []
      this.mails = []
      this.currentMail = null
      localStorage.removeItem('session_id')
      localStorage.removeItem('email')
    },

    async loadFolders() {
      if (!this.sessionId) return
      this.loading = true
      try {
        const result = await mailApi.getFolders(this.sessionId)
        this.folders = result.folders
        return result.folders
      } finally {
        this.loading = false
      }
    },

    async loadMails(folder = 'Inbox', page = 1, keyword = '') {
      if (!this.sessionId) return
      this.loading = true
      try {
        const result = await mailApi.getMails({
          session_id: this.sessionId,
          folder,
          page,
          page_size: this.pagination.pageSize,
          keyword: keyword || null
        })
        this.mails = result.mails
        this.currentFolder = folder
        this.pagination.page = page
        this.pagination.total = result.total
        return result
      } finally {
        this.loading = false
      }
    },

    async loadMailDetail(mailId) {
      if (!this.sessionId) return
      this.loading = true
      try {
        const result = await mailApi.getMailDetail(this.sessionId, mailId)
        this.currentMail = result.mail
        return result.mail
      } finally {
        this.loading = false
      }
    },

    async downloadAttachment(mailId, attachmentName) {
      if (!this.sessionId) return
      const result = await mailApi.downloadAttachment(
        this.sessionId, 
        mailId, 
        attachmentName
      )
      return result
    },

    async sendMail(data) {
      this.loading = true
      try {
        const result = await mailApi.sendMail({
          session_id: this.sessionId,
          ...data
        })
        return result
      } finally {
        this.loading = false
      }
    }
  }
})
