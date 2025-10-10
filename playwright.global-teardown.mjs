export default async function globalTeardown() {
  const procs = globalThis.__PLAYWRIGHT_SERVERS__ ?? [];
  for (const proc of procs) {
    try {
      if (!proc.killed) {
        proc.kill("SIGINT");
      }
    } catch {
      // ignore errors during shutdown
    }
  }
}
