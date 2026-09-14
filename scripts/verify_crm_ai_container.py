"""Build-independent startup regression using only disposable Docker resources.

The image argument must be built from services/crm-ai/Dockerfile. Creates a
private network and disposable PostgreSQL instance, checks real migrations,
health and migration-failure behavior, then removes only its own resources.
"""
import argparse
import subprocess
import time
from uuid import uuid4


def docker(*args, check=True):
    result = subprocess.run(["docker", *args], capture_output=True, text=True, timeout=45)
    if check and result.returncode:
        raise RuntimeError(result.stderr or result.stdout)
    return result


def wait_for(check, seconds=120):
    deadline = time.monotonic() + seconds
    while time.monotonic() < deadline:
        if check():
            return
        time.sleep(1)
    raise RuntimeError("Timed out waiting for disposable test service")


def verify(image):
    prefix = "valeo-crm-check-" + uuid4().hex[:10]
    network, database, service, broken = [prefix + suffix for suffix in ("-net", "-db", "-app", "-bad")]
    created = []
    docker("network", "create", "--internal", network)
    try:
        docker("run", "-d", "--name", database, "--network", network,
               "-e", "POSTGRES_PASSWORD=test", "-e", "POSTGRES_DB=crm_test", "postgres:15-alpine")
        created.append(database)
        wait_for(lambda: docker("exec", database, "pg_isready", "-h", "127.0.0.1", "-U", "postgres", check=False).returncode == 0)
        url = f"postgresql+asyncpg://postgres:test@{database}:5432/crm_test"
        docker("run", "-d", "--name", service, "--network", network, "-e", "DATABASE_URL=" + url, image)
        created.append(service)
        probe = "import http.client; c=http.client.HTTPConnection('localhost',6200,timeout=2); c.request('GET','/health'); assert c.getresponse().status==200"
        def healthy():
            state = docker("inspect", "-f", "{{.State.Running}}", service).stdout.strip()
            if state == "false":
                raise RuntimeError("CRM AI exited before becoming healthy")
            return docker("exec", service, "python", "-c", probe, check=False).returncode == 0
        wait_for(healthy)
        revision = docker("exec", database, "psql", "-U", "postgres", "-d", "crm_test", "-Atc", "SELECT version_num FROM alembic_version").stdout.strip()
        assert revision == "001_initial_crm_ai_schema", revision
        tables = docker("exec", database, "psql", "-U", "postgres", "-d", "crm_test", "-Atc", "SELECT count(*) FROM information_schema.tables WHERE table_schema='public' AND table_name LIKE 'crm_ai_%'").stdout.strip()
        assert tables == "5", tables
        assert docker("exec", service, "id", "-u").stdout.strip() != "0"
        docker("exec", service, "alembic", "upgrade", "head")
        print("PASS: real entrypoint, five tables, migration rerun, non-root and HTTP health", flush=True)
        # A reachable server with a wrong password produces a fast migration failure.
        docker("run", "-d", "--name", broken, "--network", network,
               "-e", "DATABASE_URL=" + url.replace(":test@", ":wrong@"), image)
        created.append(broken)
        wait_for(lambda: docker("inspect", "-f", "{{.State.Running}}", broken).stdout.strip() == "false", 30)
        code = docker("inspect", "-f", "{{.State.ExitCode}}", broken).stdout.strip()
        assert code != "0", "Migration failure must stop startup"
        print("PASS: failed migration refuses startup", flush=True)
    except Exception:
        if service in created:
            print(docker("logs", service, check=False).stderr)
        raise
    finally:
        for container in reversed(created):
            docker("rm", "-f", "-v", container, check=False)
        docker("network", "rm", network, check=False)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image")
    verify(parser.parse_args().image)
