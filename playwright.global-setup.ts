import { spawn } from "child_process";
import { fileURLToPath } from "url";
import * as path from "path";
import type { FullConfig } from "@playwright/test";

const rootDir = path.resolve(fileURLToPath(new URL("./", import.meta.url)));
const processes: ReturnType<typeof spawn>[] = [];

declare global {
  // eslint-disable-next-line no-var
  var __PLAYWRIGHT_SERVERS__: ReturnType<typeof spawn>[] | undefined;
}

async function runCommand(command: string, args: string[]): Promise<void> {
  await new Promise<void>((resolve, reject) => {
    const proc = spawn(command, args, {
      cwd: rootDir,
      stdio: "inherit",
      shell: false,
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

function startProcess(command: string, args: string[]): ReturnType<typeof spawn> {
  const proc = spawn(command, args, {
    cwd: rootDir,
    stdio: "pipe",
    shell: false,
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

async function waitForHttp(url: string, timeoutMs = 15000): Promise<void> {
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
      // retry
    }
    await new Promise((resolve) => setTimeout(resolve, 500));
  }
  throw new Error(`Timed out waiting for ${url}`);
}

export default async function globalSetup(_config: FullConfig): Promise<void> {
  const pnpmCmd = process.platform === "win32" ? "pnpm.cmd" : "pnpm";

  await runCommand(pnpmCmd, ["--filter", "frontend-web", "build"]);

  const nodeCmd = process.execPath;
  startProcess(nodeCmd, ["scripts/tmp_sse_server.js"]);
  await waitForHttp("http://localhost:5000/sse");

  startProcess(pnpmCmd, ["--filter", "frontend-web", "preview", "--", "--host", "127.0.0.1", "--port", "4173"]);
  await waitForHttp("http://localhost:4173");

  globalThis.__PLAYWRIGHT_SERVERS__ = processes;
}

