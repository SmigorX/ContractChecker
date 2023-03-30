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

function readFile(filePath) {
  return new Promise((resolve, reject) => {
    fs.readFile(filePath, 'utf-8', (err, data) => {
      if (err) {
        reject(err);
      } else {
        const dataArray = data.split(', ');
        resolve(dataArray);
      }
    });
  });
}

ipcMain.on('read-file', async (event, filePath) => {
  try {
    const dataArray = await readFile(filePath);
    event.reply('read-file-reply', dataArray);
  } catch (err) {
    event.reply('read-file-reply', err.message);
  }
});

app.whenReady().then(() => {
  createWindow();
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

