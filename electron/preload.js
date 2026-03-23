const { contextBridge, ipcRenderer } = require('electron')

// 暴露安全的 API 给渲染进程
contextBridge.exposeInMainWorld('electronAPI', {
  // 存储
  store: {
    set: (key, value) => ipcRenderer.invoke('store:set', key, value),
    get: (key) => ipcRenderer.invoke('store:get', key),
    delete: (key) => ipcRenderer.invoke('store:delete', key)
  },
  
  // 对话框
  dialog: {
    selectFolder: () => ipcRenderer.invoke('dialog:selectFolder'),
    selectFile: () => ipcRenderer.invoke('dialog:selectFile')
  },
  
  // 文件操作
  file: {
    save: (defaultName, content) => ipcRenderer.invoke('file:save', defaultName, content),
    read: (filePath) => ipcRenderer.invoke('file:read', filePath)
  }
})
