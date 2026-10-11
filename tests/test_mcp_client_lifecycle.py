"""Real stdio child-process probes: no DB, network or Docker."""
import asyncio
import os
import subprocess

import pytest

from app.integrations.mcp_client import MCPClient


@pytest.fixture
def server(tmp_path):
    script = tmp_path / "stdio-server.cjs"
    script.write_text(r'''
const readline = require('node:readline');
const fs = require('node:fs');
readline.createInterface({ input: process.stdin }).on('line', line => {
  const request = JSON.parse(line);
  const mode = request.params.arguments.mode;
  fs.writeFileSync(request.params.arguments.pidfile, String(process.pid));
  const result = { content: [{ type: 'text', text: 'Grün' }] };
  const send = data => process.stdout.write(JSON.stringify(data) + '\n');
  setInterval(() => {}, 1000); // Deliberately stays alive after responding.
  if (mode === 'hang') return;
  if (mode === 'ignore-term') { process.on('SIGTERM', () => {}); return; }
  if (mode === 'exit') { process.exit(1); }
  if (mode === 'bad-json') { process.stdout.write('private input: broken JSON\n'); return; }
  if (mode === 'stderr') process.stderr.write('private input\n'.repeat(100000));
  if (mode === 'notification') send({ jsonrpc: '2.0', method: 'notifications/progress', params: {} });
  if (mode === 'error') { send({ jsonrpc: '2.0', id: request.id, error: { message: 'private input' } }); return; }
  if (mode === 'invalid-result') { send({ jsonrpc: '2.0', id: request.id, result: [] }); return; }
  const id = mode === 'wrong-id' ? 99 : mode === 'bool-id' ? true : request.id;
  const jsonrpc = mode === 'wrong-version' ? '1.0' : '2.0';
  setTimeout(() => send({ jsonrpc, id, result }), mode === 'slow' ? 200 : 0);
});
''', encoding="utf-8")
    return script, tmp_path / "pid.txt"


def assert_stopped(pidfile):
    pid = int(pidfile.read_text())
    if os.name == "nt":
        # Query only this child's PID; never stop unrelated processes.
        result = subprocess.run(
            ["tasklist", "/FI", f"PID eq {pid}", "/FO", "CSV", "/NH"],
            capture_output=True, text=True, check=True,
        )
        assert f'"{pid}"' not in result.stdout
    else:
        with pytest.raises(ProcessLookupError):
            os.kill(pid, 0)


def run_call(server, mode, timeout=3):
    script, pidfile = server
    result = asyncio.run(MCPClient(script, timeout=timeout).call_tool(
        "local-probe", "probe", {"mode": mode, "pidfile": str(pidfile)}
    ))
    assert_stopped(pidfile)
    return result


@pytest.mark.parametrize("mode", ["success", "notification", "stderr"])
def test_success_always_reaps_child(server, mode):
    assert run_call(server, mode) == {"content": [{"type": "text", "text": "Grün"}]}


@pytest.mark.parametrize("mode", ["bad-json", "wrong-id", "bool-id", "wrong-version", "error", "invalid-result", "exit"])
def test_fail_closed_without_private_response_logs(server, mode, caplog):
    assert run_call(server, mode) is None
    assert "private input" not in caplog.text


def test_timeout_reaps_child(server):
    assert run_call(server, "hang", timeout=1) is None


def test_shutdown_escalates_when_terminate_is_ignored(server):
    # POSIX exercises the kill fallback; Windows terminate already forces exit.
    assert run_call(server, "ignore-term", timeout=1) is None


def test_event_loop_keeps_running(server):
    script, pidfile = server
    async def scenario():
        task = asyncio.create_task(MCPClient(script).call_tool(
            "local-probe", "probe", {"mode": "slow", "pidfile": str(pidfile)}
        ))
        ticks = 0
        while not task.done():
            await asyncio.sleep(0.01)
            ticks += 1
        assert await task
        assert ticks >= 10
    asyncio.run(scenario())
    assert_stopped(pidfile)


def test_cancellation_is_propagated_after_reaping_child(server):
    script, pidfile = server
    async def scenario():
        task = asyncio.create_task(MCPClient(script).call_tool(
            "local-probe", "probe", {"mode": "hang", "pidfile": str(pidfile)}
        ))
        async with asyncio.timeout(5):
            while not pidfile.exists():
                await asyncio.sleep(0.01)
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task
    asyncio.run(scenario())
    assert_stopped(pidfile)


@pytest.mark.parametrize("timeout", [0, -1, float("nan"), float("inf")])
def test_invalid_timeout_rejected(timeout):
    with pytest.raises(ValueError):
        MCPClient(timeout=timeout)


def test_missing_server_is_optional(tmp_path):
    assert asyncio.run(MCPClient(tmp_path / "missing.cjs").call_tool("probe", "probe", {})) is None
