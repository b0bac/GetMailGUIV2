const { app, BrowserWindow, ipcMain, dialog } = require('electron')
const path = require('path')
const fs = require('fs')
const Store = require('electron-store')

// 持久化存储
const store = new Store()

let mainWindow

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1400,
    height: 900,
    minWidth: 1200,
    minHeight: 700,
    frame: true,
    backgroundColor: '#1a1a2e',
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: path.join(__dirname, 'preload.js')
    },
    icon: path.join(__dirname, '../build/icon.png')
  })

  // 开发环境
  if (process.env.NODE_ENV === 'development' || !app.isPackaged) {
    mainWindow.loadURL('http://localhost:3000')
    mainWindow.webContents.openDevTools()
  } else {
    mainWindow.loadFile(path.join(__dirname, '../dist/index.html'))
  }

  mainWindow.on('closed', () => {
    mainWindow = null
  })
}

app.whenReady().then(() => {
  createWindow()

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow()
    }
  })
})

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit()
  }
})

// ==================== IPC 通信 ====================

// 保存配置
ipcMain.handle('store:set', async (event, key, value) => {
  store.set(key, value)
  return true
})

// 读取配置
ipcMain.handle('store:get', async (event, key) => {
  return store.get(key)
})

// 删除配置
ipcMain.handle('store:delete', async (event, key) => {
  store.delete(key)
  return true
})

// 选择目录
ipcMain.handle('dialog:selectFolder', async () => {
  const result = await dialog.showOpenDialog(mainWindow, {
    properties: ['openDirectory', 'createDirectory']
  })
  return result.filePaths[0] || null
})

// 选择文件
ipcMain.handle('dialog:selectFile', async () => {
  const result = await dialog.showOpenDialog(mainWindow, {
    properties: ['openFile', 'multiSelections']
  })
  return result.filePaths || []
})

// 保存文件
ipcMain.handle('file:save', async (event, defaultName, content) => {
  const result = await dialog.showSaveDialog(mainWindow, {
    defaultPath: defaultName,
    filters: [
      { name: 'All Files', extensions: ['*'] }
    ]
  })
  
  if (result.filePath) {
    fs.writeFileSync(result.filePath, content)
    return result.filePath
  }
  return null
})

// 读取文件
ipcMain.handle('file:read', async (event, filePath) => {
  try {
    const content = fs.readFileSync(filePath)
    return {
      success: true,
      data: content.toString('base64')
    }
  } catch (error) {
    return {
      success: false,
      error: error.message
    }
  }
})
