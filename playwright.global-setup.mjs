import { spawn } from "child_process";
import { mkdirSync, writeFileSync } from "fs";
import { fileURLToPath } from "url";
import path from "path";

const rootDir = path.resolve(fileURLToPath(new URL("./", import.meta.url)));
const processes = [];
const isWindows = process.platform === "win32";
const pidFile = path.join(rootDir, "playwright-tests", "artifacts", "server-pids.json");

// Ziel-URLs identisch zur baseURL-Aufloesung in playwright.config.ts aufloesen,
// damit der Reuse-Check exakt den Server prueft, gegen den die Tests laufen.
const frontendUrl = process.env.VALEO_BASE_URL ?? process.env.FRONTEND_URL ?? "http://127.0.0.1:4173";
const previewPort = process.env.PLAYWRIGHT_PREVIEW_PORT ?? "4173";
const sseUrl = process.env.PLAYWRIGHT_SSE_URL ?? "http://localhost:5000/sse";

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
    detached: true,
    stdio: "ignore",
    windowsHide: true,
  });
  proc.unref();
  processes.push(proc);
  return proc;
}

// Schneller, nicht-blockierender Erreichbarkeits-Check (HEAD).
async function isReachable(url, timeoutMs = 2000) {
  try {
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), timeoutMs);
    const response = await fetch(url, { method: "HEAD", signal: controller.signal });
    clearTimeout(timeout);
    return response.ok || response.status === 404;
  } catch {
    return false;
  }
}

async function waitForHttp(url, timeoutMs = 15000) {
  const started = Date.now();
  while (Date.now() - started < timeoutMs) {
    if (await isReachable(url, 3000)) {
      return;
    }
    await new Promise((resolve) => setTimeout(resolve, 500));
  }
  throw new Error(`Timed out waiting for ${url}`);
}

/**
 * Best-Practice "reuse existing server" (analog Playwrights webServer.reuseExistingServer):
 * Ist ein Server bereits erreichbar (z. B. laufender Docker-Dev-Stack oder Vorlauf eines
 * anderen Runs), wird er WIEDERVERWENDET statt ein zweites Mal auf denselben Port gebunden
 * zu werden (= Quelle des frueheren Port-Konflikts). Nur selbst gestartete Prozesse landen
 * in `processes` und damit in der PID-Datei, sodass das Teardown ausschliesslich eigene
 * Server beendet und niemals einen fremden, weiterlaufenden Dev-Stack abschiesst.
 * Erzwingen eines frischen Spawns trotz laufender Server: PLAYWRIGHT_FORCE_SPAWN=1.
 */
const forceSpawn = process.env.PLAYWRIGHT_FORCE_SPAWN === "1";

export default async function globalSetup() {
  const pnpmCmd = "pnpm";
  const nodeCmd = process.execPath;

  // ── Frontend ────────────────────────────────────────────────────────────────
  // Grosszuegiges Reuse-Timeout: ein laufender Vite-Dev-Container kann beim ersten
  // Request kalt sein (~10s erste Antwort), waehrend ein geschlossener Port sofort
  // mit ECONNREFUSED scheitert — langes Timeout verzoegert den Spawn-Pfad also nicht.
  const frontendProbeMs = Number(process.env.PLAYWRIGHT_FRONTEND_PROBE_MS ?? "20000");
  const frontendUp = !forceSpawn && (await isReachable(frontendUrl, frontendProbeMs));
  if (frontendUp) {
    console.log(`[global-setup] Frontend bereits erreichbar (${frontendUrl}) — wiederverwendet, kein Build/Preview-Start.`);
  } else {
    await runCommand(pnpmCmd, ["--filter", "frontend-web", "build"]);
    startProcess(pnpmCmd, ["--filter", "frontend-web", "preview", "--", "--host", "127.0.0.1", "--port", previewPort]);
    await waitForHttp(`http://127.0.0.1:${previewPort}`);
  }

  // ── SSE-Stub ──────────────────────────────────────────────────────────────────
  const sseUp = !forceSpawn && (await isReachable(sseUrl));
  if (sseUp) {
    console.log(`[global-setup] SSE bereits erreichbar (${sseUrl}) — wiederverwendet.`);
  } else {
    startProcess(nodeCmd, ["scripts/tmp_sse_server.js"]);
    await waitForHttp(sseUrl);
  }

  mkdirSync(path.dirname(pidFile), { recursive: true });
  writeFileSync(pidFile, JSON.stringify(processes.map((proc) => proc.pid).filter(Boolean)));
}
