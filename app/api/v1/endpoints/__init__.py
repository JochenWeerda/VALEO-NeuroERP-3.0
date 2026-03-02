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
from . import sales_orders
from . import docflow
from .warehouses import router as warehouses
from . import gap
from . import prospecting
from .chart_of_accounts import router as chart_of_accounts
from . import policies
from . import finance_invoices
from . import audit
from . import accounting_periods
from . import payment_matching
from . import ap_invoices
from . import bank_accounts
from . import debtors
from . import open_items
from . import bank_statement_import
from . import bank_reconciliation
from . import tax_keys
from . import subsidiary_ledger_reconciliation
from . import financial_reports
from . import bulk_journal_import
from . import exchange_rates
from . import booking_templates
from . import dunning
from . import ap_approval_workflow
from . import payment_runs
from . import auto_matching
from . import vat_return_export
from . import closing_checklists
from . import iban_lookup
from . import credit_debit_memos
from . import portal_shop
from . import opportunities
from . import cases
# L3-Connect gap closure endpoints
from . import inventory_counts
from . import weighing_tickets
from . import warehouse_transfers
from . import preparation_lists
from . import pick_lists
from . import gs1_parser
from . import nve
from . import webhooks
from . import article_extensions
from . import customer_extensions
from . import business_partners
from . import messages
from . import dms_images
from . import sales_shipping_ext
from . import master_data
from . import compat
from . import modules
from . import agrar_contracts
from . import agrar_varieties
from . import silo
from . import agrar_settlements
from . import harvest_acceptance
from . import quality_protocols
from . import daily_prices
from . import self_billing
from . import nawaro
from . import nawaro_raps
from . import einkauf_lieferschein
from . import admin_monitoring
from . import admin_core
from . import admin_pos
from . import admin_devices
from . import admin_mobile
from . import admin_reporting
from . import controlling
from . import training
from . import personal
from . import analytics
from . import sales_delivery_notes
from . import branches
from . import pricing
from . import config_service
from . import job_runner
from . import finance_actions
from . import lohn_connector
from . import quadriga_connector
from . import asset_ledger_connector
from . import fibu_connectors
from . import gobd_archiv
