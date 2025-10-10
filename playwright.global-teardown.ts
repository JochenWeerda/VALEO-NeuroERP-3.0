import type { FullConfig } from "@playwright/test";

declare global {
  // eslint-disable-next-line no-var
  var __PLAYWRIGHT_SERVERS__: import("child_process").ChildProcess[] | undefined;
}

export default async function globalTeardown(_config: FullConfig): Promise<void> {
  const procs = globalThis.__PLAYWRIGHT_SERVERS__ ?? [];
  for (const proc of procs) {
    try {
      if (!proc.killed) {
        proc.kill("SIGINT");
      }
    } catch {
      // ignore
    }
  }
}
