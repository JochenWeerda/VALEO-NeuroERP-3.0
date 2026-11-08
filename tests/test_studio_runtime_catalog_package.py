"""Studio authoring/release must receive its canonical schema catalog in deployment."""
from pathlib import Path
import yaml

ROOT=Path(__file__).resolve().parents[1]
CATALOG='docs/admin/table-catalog.json'


def test_backend_image_packages_only_the_required_schema_contract():
    dockerfile=(ROOT/'Dockerfile.backend').read_text(encoding='utf-8')
    assert 'COPY --chown=appuser:appuser '+CATALOG+' ./'+CATALOG in dockerfile
    assert dockerfile.count('COPY --chown=appuser:appuser config/ ./config/')==1
    assert (ROOT/CATALOG).is_file()
    ignore=(ROOT/'.dockerignore').read_text(encoding='utf-8').splitlines()
    assert 'docs' not in ignore
    assert 'docs/**' in ignore
    assert '!docs/admin/' in ignore and '!'+CATALOG in ignore
    assert ignore.index('!docs/admin/') < ignore.index('docs/admin/**') < ignore.index('!'+CATALOG)
    assert '!.env' not in ignore and '.env' in ignore


def test_compose_mounts_the_same_schema_contract_read_only():
    compose=yaml.safe_load((ROOT/'docker-compose.yml').read_text(encoding='utf-8'))
    volumes=compose['services']['backend']['volumes']
    assert './'+CATALOG+':/app/'+CATALOG+':ro' in volumes
