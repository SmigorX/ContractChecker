const { ipcRenderer } = require('electron');

// Wait for the DOM to be loaded before running the code
window.addEventListener('DOMContentLoaded', () => {
  const fileContentElement = document.getElementById('file-content');

  ipcRenderer.on('read-file-reply', (event, fileData) => {
    if (typeof fileData === 'string') {
      fileContentElement.textContent = `Error: ${fileData}`;
    } else {
      fileContentElement.innerHTML = fileData.join('<br>');
    }
  });

  ipcRenderer.send('read-file', './programs/stock.txt');
});