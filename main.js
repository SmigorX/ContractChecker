const { app, BrowserWindow, ipcMain } = require('electron');
const fs = require('fs');

let mainWindow;

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 800,
    height: 600,
    autoHideMenuBar: true,
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false,
      enableRemoteModule: true,
    },
  });

  mainWindow.loadFile('./static/index.html');

  mainWindow.on('closed', function () {
    mainWindow = null
  });
}

ipcMain.on('read-file', (event, filePath) => {
  fs.readFile(filePath, 'utf-8', (err, data) => {
    if (err) {
      event.reply('read-file-reply', err.message);
    } else {
      event.reply('read-file-reply', data);
    }
  });
});

app.whenReady().then(() => {
  createWindow();
});


app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

