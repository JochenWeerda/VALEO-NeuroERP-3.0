# VALEO-NeuroERP API v1 Endpoints Package

from .health import router as health
from .tenants import router as tenants
from .users import router as users
from .customers import router as customers
from .leads import router as leads
from .contacts import router as contacts
from . import activities
from . import farm_profiles
from .accounts import router as accounts
from .journal_entries import router as journal_entries
from .articles import router as articles
from .warehouses import router as warehouses
from . import gap
from . import prospecting
from .chart_of_accounts import router as chart_of_accounts
from . import policies