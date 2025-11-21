import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PACKAGE_SRC = ROOT / "packages" / "finance-shared" / "src"
if str(PACKAGE_SRC) not in sys.path:
    sys.path.insert(0, str(PACKAGE_SRC))


