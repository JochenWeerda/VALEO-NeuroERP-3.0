import { spawn } from "child_process";
import { fileURLToPath } from "url";
import path from "path";

const rootDir = path.resolve(fileURLToPath(new URL("./", import.meta.url)));
const processes = [];
const isWindows = process.platform === "win32";

function toSpawn(command, args) {
  if (isWindows) {
    const quoted = args.map((arg) => (arg.includes(" ") ? `"${arg}"` : arg));
    return { cmd: "cmd.exe", args: ["/c", command, ...quoted] };
  }
  return { cmd: command, args };
}

async function runCommand(command, args) {
  const { cmd, args: finalArgs } = toSpawn(command, args);
  await new Promise((resolve, reject) => {
    const proc = spawn(cmd, finalArgs, {
      cwd: rootDir,
      stdio: "inherit",
    });
    proc.on("exit", (code) => {
      if (code === 0) {
        resolve();
      } else {
        reject(new Error(`${command} ${args.join(" ")} exited with code ${code}`));
      }
    });
    proc.on("error", reject);
  });
}

function startProcess(command, args) {
  const { cmd, args: finalArgs } = toSpawn(command, args);
  const proc = spawn(cmd, finalArgs, {
    cwd: rootDir,
    stdio: "pipe",
  });
  proc.stdout?.on("data", (chunk) => {
    process.stdout.write(chunk);
  });
  proc.stderr?.on("data", (chunk) => {
    process.stderr.write(chunk);
  });
  processes.push(proc);
  return proc;
}

async function waitForHttp(url, timeoutMs = 15000) {
  const started = Date.now();
  while (Date.now() - started < timeoutMs) {
    try {
      const controller = new AbortController();
      const timeout = setTimeout(() => controller.abort(), 3000);
      const response = await fetch(url, { method: "HEAD", signal: controller.signal });
      clearTimeout(timeout);
      if (response.ok || response.status === 404) {
        return;
      }
    } catch {
      // retry until timeout
    }
    await new Promise((resolve) => setTimeout(resolve, 500));
  }
  throw new Error(`Timed out waiting for ${url}`);
}

export default async function globalSetup() {
  const pnpmCmd = isWindows ? "pnpm" : "pnpm";

  await runCommand(pnpmCmd, ["--filter", "frontend-web", "build"]);

  const nodeCmd = process.execPath;
  startProcess(nodeCmd, ["scripts/tmp_sse_server.js"]);
  await waitForHttp("http://localhost:5000/sse");

  startProcess(pnpmCmd, ["--filter", "frontend-web", "preview", "--", "--host", "127.0.0.1", "--port", "4173"]);
  await waitForHttp("http://localhost:4173");

  globalThis.__PLAYWRIGHT_SERVERS__ = processes;
}
