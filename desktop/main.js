const { app, BrowserWindow, dialog, shell } = require("electron");
const { spawn } = require("node:child_process");
const fs = require("node:fs");
const http = require("node:http");
const path = require("node:path");

const APP_URL = "http://127.0.0.1:5050";
const HEALTH_URL = `${APP_URL}/api/health`;
const SERVER_TIMEOUT_MS = 30000;

let mainWindow = null;
let flaskProcess = null;

function projectRoot() {
  if (app.isPackaged) {
    return path.join(process.resourcesPath, "app");
  }
  return path.resolve(__dirname, "..");
}

function pythonExecutable(root = projectRoot()) {
  const localPython = process.platform === "win32"
    ? path.join(root, ".venv", "Scripts", "python.exe")
    : path.join(root, ".venv", "bin", "python");

  if (fs.existsSync(localPython)) {
    return localPython;
  }

  return process.platform === "win32" ? "python" : "python3";
}

function requestOk(url) {
  return new Promise((resolve) => {
    const request = http.get(url, { timeout: 2000 }, (response) => {
      response.resume();
      resolve(response.statusCode >= 200 && response.statusCode < 500);
    });
    request.on("timeout", () => {
      request.destroy();
      resolve(false);
    });
    request.on("error", () => resolve(false));
  });
}

async function waitForServer(timeoutMs = SERVER_TIMEOUT_MS) {
  const startedAt = Date.now();
  while (Date.now() - startedAt < timeoutMs) {
    if (await requestOk(HEALTH_URL)) {
      return true;
    }
    await new Promise((resolve) => setTimeout(resolve, 500));
  }
  return false;
}

async function ensureFlaskServer() {
  if (await requestOk(HEALTH_URL)) {
    return;
  }

  const root = projectRoot();
  const logPath = path.join(root, "desktop-server.log");
  const errorPath = path.join(root, "desktop-server.err.log");
  const out = fs.openSync(logPath, "a");
  const err = fs.openSync(errorPath, "a");

  flaskProcess = spawn(pythonExecutable(root), ["-m", "src.web_app"], {
    cwd: root,
    env: { ...process.env },
    stdio: ["ignore", out, err],
    windowsHide: true
  });

  flaskProcess.on("exit", () => {
    flaskProcess = null;
  });

  const ready = await waitForServer();
  if (!ready) {
    throw new Error(`The local Flask server did not become ready at ${APP_URL}. Check ${errorPath}.`);
  }
}

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1440,
    height: 940,
    minWidth: 1100,
    minHeight: 760,
    backgroundColor: "#030807",
    title: "Prediction Market Bot",
    autoHideMenuBar: true,
    webPreferences: {
      contextIsolation: true,
      nodeIntegration: false,
      sandbox: true
    }
  });

  mainWindow.loadURL(APP_URL);

  mainWindow.webContents.setWindowOpenHandler(({ url }) => {
    shell.openExternal(url);
    return { action: "deny" };
  });

  mainWindow.webContents.on("will-navigate", (event, url) => {
    if (!url.startsWith(APP_URL)) {
      event.preventDefault();
      shell.openExternal(url);
    }
  });
}

app.whenReady().then(async () => {
  try {
    await ensureFlaskServer();
    createWindow();
  } catch (error) {
    dialog.showErrorBox("Prediction Market Bot failed to start", error.message);
    app.quit();
  }
});

app.on("window-all-closed", () => {
  if (process.platform !== "darwin") {
    app.quit();
  }
});

app.on("activate", () => {
  if (BrowserWindow.getAllWindows().length === 0) {
    createWindow();
  }
});

app.on("before-quit", () => {
  if (flaskProcess) {
    flaskProcess.kill();
    flaskProcess = null;
  }
});
