"""Run existing KI contracts in their own app namespace; preserve all core evidence."""
from __future__ import annotations

import configparser
import io
import os
from pathlib import Path
import shlex
import shutil
import subprocess
import sys
import tempfile

from coverage import Coverage, CoverageData


def minimum(root: Path) -> float:
    config = configparser.ConfigParser()
    config.read(root / 'pytest.ini', encoding='utf-8')
    values = [arg.split('=', 1)[1] for arg in shlex.split(config['pytest']['addopts'])
              if arg.startswith('--cov-fail-under=')]
    if len(values) != 1 or not 0 < float(values[0]) <= 100:
        raise ValueError('One positive existing backend coverage minimum is required')
    return float(values[0])


def run(root: Path) -> float:
    root = root.resolve()
    floor = minimum(root)
    core_file = root / '.coverage'
    if not core_file.is_file():
        raise ValueError('Full core suite coverage is required before service contracts')
    core = CoverageData(basename=str(core_file))
    core.read()
    original_files = set(core.measured_files())
    if not original_files:
        raise ValueError('Core coverage is empty')
    service = root / 'services/ki-usability'
    artifacts = root / 'artifacts'
    artifacts.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='ki-contracts-', dir=artifacts) as temporary:
        scratch = Path(temporary)
        config = scratch / 'pytest.ini'
        config.write_text('[pytest]\n', encoding='utf-8')
        service_file = scratch / '.coverage.service'
        env = os.environ.copy()
        for name in tuple(env):
            if name.startswith('COV_CORE_') or name == 'COVERAGE_PROCESS_START':
                env.pop(name)
        # Each service owns an app package. Never import the ERP app in this child.
        env['PYTHONPATH'] = str(service)
        env['COVERAGE_FILE'] = str(service_file)
        args = [sys.executable, '-m', 'pytest', '-c', str(config), 'tests', '-q',
                '--cov=app', '--cov-report=']
        if core.has_arcs():
            args.append('--cov-branch')
        subprocess.run(args, cwd=service, env=env, check=True)
        child = CoverageData(basename=str(service_file))
        child.read()
        service_root = (service / 'app').resolve()
        child_files = set(child.measured_files())
        if not child_files or any(not Path(name).resolve().is_relative_to(service_root) for name in child_files):
            raise ValueError('Service coverage is empty or escaped its own app namespace')
        if child.has_arcs() != core.has_arcs():
            raise ValueError('Core and service coverage modes disagree')
        merged_file = scratch / '.coverage.merged'
        merged = Coverage(data_file=str(merged_file), config_file=False,
                          source=[str(root / name) for name in ('app', 'modules', 'services')])
        data = merged.get_data()
        data.update(core)
        data.update(child)
        if not original_files.issubset(data.measured_files()):
            raise ValueError('Merging lost core source files')
        for name in original_files:
            if not set(core.lines(name) or ()).issubset(data.lines(name) or ()):
                raise ValueError('Merging lost core executed lines')
            if core.has_arcs() and not set(core.arcs(name) or ()).issubset(data.arcs(name) or ()):
                raise ValueError('Merging lost core branches')
        percentage = merged.report(file=io.StringIO())
        if percentage < floor:
            raise ValueError(f'Merged coverage {percentage:.2f}% is below the unchanged {floor:g}% minimum')
        xml = scratch / 'coverage.xml'
        merged.xml_report(outfile=str(xml))
        merged.save()
        # Publish only after test success, scope checks, preservation and the gate.
        shutil.copyfile(merged_file, core_file)
        shutil.copyfile(xml, root / 'coverage.xml')
    print(f'Core evidence preserved; KI service included; merged coverage {percentage:.2f}% >= {floor:g}%')
    return percentage


if __name__ == '__main__':
    run(Path(__file__).resolve().parents[1])
