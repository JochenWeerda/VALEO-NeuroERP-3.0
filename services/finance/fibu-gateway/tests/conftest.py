import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
PACKAGE_SRC = ROOT / "packages" / "finance-shared" / "src"
if str(PACKAGE_SRC) not in sys.path:
    sys.path.insert(0, str(PACKAGE_SRC))

SERVICE_SRC = ROOT / "services" / "finance" / "fibu-gateway"
if str(SERVICE_SRC) not in sys.path:
    sys.path.insert(0, str(SERVICE_SRC))

