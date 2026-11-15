FROM python:3.11.18-slim-bookworm AS python-runtime
FROM node:24-bookworm

ENV DEBIAN_FRONTEND=noninteractive \
    CI=true \
    HUSKY=0 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH=/opt/venv/bin:$PATH

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       build-essential \
       ca-certificates \
       git \
       libpq-dev \
       libbz2-1.0 libffi8 libgdbm6 liblzma5 libncursesw6 libreadline8 libsqlite3-0 libssl3 libuuid1 zlib1g \
    && rm -rf /var/lib/apt/lists/*

# Bookworm's distro Python 3.11.2 cannot install the security-pinned Soup Sieve.
# Both official images use bookworm; preserve Node 24 and take Python's complete
# /usr/local runtime (including its shared library and venv support).
COPY --from=python-runtime /usr/local/ /usr/local/
RUN ldconfig \
    && python3 -c "import sys, bz2, ctypes, lzma, sqlite3, ssl, venv; assert sys.version_info >= (3, 11, 5), sys.version" \
    && node --version

# Scanner contract: Anthropic supplies the repository as the build context and
# expects the complete checkout at /src. Dependency downloads happen while the
# image is built; the subsequent security analysis runs without network access.
COPY . /src
WORKDIR /src

RUN python3 -m venv /opt/venv \
    && python -m pip install --no-cache-dir --upgrade pip setuptools wheel \
    && python -m pip install --no-cache-dir -r requirements.txt

RUN corepack enable \
    && corepack prepare pnpm@9.12.0 --activate \
    && pnpm install --frozen-lockfile

# Compile Python strictly. The repository-wide TypeScript build currently has
# known baseline failures in legacy workspace packages; keep those diagnostics
# visible without withholding the complete source/dependency image from the
# security scanner.
RUN python -m compileall -q app modules packages services

RUN pnpm build \
    || echo "WARNING: OSS Scanner workspace build reported baseline failures"

# These fast, security-focused checks need no external service. A test failure
# remains visible in the build log but does not prevent Anthropic from scanning
# the prepared source and dependency tree.
RUN timeout 180s python -m pytest -q --no-cov \
      tests/test_auth_middleware.py \
      tests/test_tenant_enforcement.py \
      tests/test_mcp_oidc_verification.py \
    || echo "WARNING: OSS Scanner Python smoke tests reported failures"

RUN timeout 180s pnpm --filter @valero-neuroerp/frontend-web exec vitest run \
      src/__tests__/lib/omnibox/command-safety.test.ts \
    || echo "WARNING: OSS Scanner frontend smoke test reported failures"
