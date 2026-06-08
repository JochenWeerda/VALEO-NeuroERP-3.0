import { spawnSync } from "child_process";
import { existsSync, readFileSync, rmSync } from "fs";
import { fileURLToPath } from "url";
import path from "path";

const rootDir = path.resolve(fileURLToPath(new URL("./", import.meta.url)));
const pidFile = path.join(rootDir, "playwright-tests", "artifacts", "server-pids.json");

export default async function globalTeardown() {
  const pids = existsSync(pidFile) ? JSON.parse(readFileSync(pidFile, "utf8")) : [];

  for (const pid of pids) {
    try {
      if (process.platform === "win32") {
        spawnSync("taskkill", ["/PID", String(pid), "/T", "/F"], {
          stdio: "ignore",
          timeout: 10000,
        });
      } else {
        process.kill(pid, "SIGINT");
      }
    } catch {
      // Teardown remains best-effort; stale PIDs may already be gone.
    }
  }

  rmSync(pidFile, { force: true });
}
