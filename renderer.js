const { ipcRenderer} = require('electron');

// Use stuff like this to make absolute paths
// path.join(app.getAppPath(), '..', 'python_scripts/my_script.py'


window.addEventListener('DOMContentLoaded', () => {
  const fileContentElement = document.getElementById('file-content');


  ipcRenderer.on('read-file-reply', (event, fileData) => {
    if (typeof fileData === 'string') {
      const lines = fileData.split('\n');
      lines.forEach(line => {
        const lineElement = document.createElement('div');
        lineElement.textContent = line;
        fileContentElement.appendChild(lineElement);
      });
    } else {
      fileContentElement.innerHTML = "Error";
    }
  });

  ipcRenderer.send('read-file', './programs/stock.txt');

});
