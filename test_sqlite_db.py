#!/usr/bin/env python3
"""
Test script for VALEO-NeuroERP SQLite database setup
"""

import sqlite3
import os
from pathlib import Path

def test_sqlite_database():
    """Test SQLite database creation and basic operations"""

    # Database file path
    db_path = "valeo_neuro_erp.db"

    # Remove existing database if it exists
    if os.path.exists(db_path):
        os.remove(db_path)
        print(f"Removed existing database: {db_path}")

    try:
        # Connect to SQLite database (creates it if it doesn't exist)
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        print(f"Successfully connected to SQLite database: {db_path}")

        # Create tables using table prefixes instead of schemas
        tables_sql = """
        -- Shared tables
        CREATE TABLE shared_tenants (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            domain TEXT,
            is_active INTEGER DEFAULT 1,
            settings TEXT DEFAULT '{}',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE shared_users (
            id TEXT PRIMARY KEY,
            keycloak_id TEXT NOT NULL,
            username TEXT NOT NULL,
            email TEXT NOT NULL,
            first_name TEXT,
            last_name TEXT,
            is_active INTEGER DEFAULT 1,
            roles TEXT,
            tenant_id TEXT,
            preferences TEXT DEFAULT '{}',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (tenant_id) REFERENCES shared_tenants(id),
            UNIQUE (email),
            UNIQUE (keycloak_id),
            UNIQUE (username)
        );

        -- CRM tables
        CREATE TABLE crm_customers (
            id TEXT PRIMARY KEY,
            tenant_id TEXT,
            customer_number TEXT NOT NULL,
            company_name TEXT,
            contact_person TEXT,
            email TEXT,
            phone TEXT,
            address TEXT,
            customer_type TEXT DEFAULT 'business',
            credit_limit REAL DEFAULT 0,
            payment_terms TEXT,
            is_active INTEGER DEFAULT 1,
            notes TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            created_by TEXT,
            updated_by TEXT,
            FOREIGN KEY (tenant_id) REFERENCES shared_tenants(id),
            FOREIGN KEY (created_by) REFERENCES shared_users(id),
            FOREIGN KEY (updated_by) REFERENCES shared_users(id),
            UNIQUE (customer_number)
        );

        -- ERP tables
        CREATE TABLE erp_chart_of_accounts (
            id TEXT PRIMARY KEY,
            tenant_id TEXT,
            account_number TEXT NOT NULL,
            account_name TEXT NOT NULL,
            account_type TEXT NOT NULL,
            category TEXT,
            is_active INTEGER DEFAULT 1,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (tenant_id) REFERENCES shared_tenants(id),
            UNIQUE (account_number)
        );

        CREATE TABLE erp_journal_entries (
            id TEXT PRIMARY KEY,
            tenant_id TEXT,
            entry_number TEXT NOT NULL,
            entry_date DATE NOT NULL,
            posting_date DATE NOT NULL,
            document_type TEXT,
            document_number TEXT,
            reference TEXT,
            description TEXT,
            total_debit REAL DEFAULT 0,
            total_credit REAL DEFAULT 0,
            status TEXT DEFAULT 'draft',
            posted_by TEXT,
            posted_at DATETIME,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (tenant_id) REFERENCES shared_tenants(id),
            FOREIGN KEY (posted_by) REFERENCES shared_users(id),
            UNIQUE (entry_number)
        );

        -- Inventory tables
        CREATE TABLE inventory_warehouses (
            id TEXT PRIMARY KEY,
            tenant_id TEXT,
            warehouse_code TEXT NOT NULL,
            name TEXT NOT NULL,
            address TEXT,
            is_active INTEGER DEFAULT 1,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (tenant_id) REFERENCES shared_tenants(id),
            UNIQUE (warehouse_code)
        );

        CREATE TABLE inventory_articles (
            id TEXT PRIMARY KEY,
            tenant_id TEXT,
            article_number TEXT NOT NULL,
            name TEXT NOT NULL,
            description TEXT,
            unit TEXT DEFAULT 'pcs',
            category TEXT,
            purchase_price REAL,
            sales_price REAL,
            minimum_stock INTEGER DEFAULT 0,
            maximum_stock INTEGER,
            current_stock INTEGER DEFAULT 0,
            is_active INTEGER DEFAULT 1,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (tenant_id) REFERENCES shared_tenants(id),
            UNIQUE (article_number)
        );
        """

        # Execute table creation
        cursor.executescript(tables_sql)
        print("Successfully created all database tables")

        # Insert sample data
        sample_data_sql = """
        INSERT INTO shared_tenants (id, name, domain, settings) VALUES
        ('550e8400-e29b-41d4-a716-446655440000', 'VALEO Default', 'valeo-neuro-erp.com', '{}');

        INSERT INTO shared_users (id, keycloak_id, username, email, first_name, last_name, roles) VALUES
        ('550e8400-e29b-41d4-a716-446655440001', 'admin-keycloak-id', 'admin', 'admin@valeo-neuro-erp.com', 'System', 'Administrator', '["admin", "user"]');

        INSERT INTO erp_chart_of_accounts (tenant_id, account_number, account_name, account_type, category) VALUES
        ('550e8400-e29b-41d4-a716-446655440000', '1000', 'Kasse', 'asset', 'current_assets'),
        ('550e8400-e29b-41d4-a716-446655440000', '1200', 'Bank', 'asset', 'current_assets'),
        ('550e8400-e29b-41d4-a716-446655440000', '4000', 'Umsatzerlöse', 'revenue', 'revenue');

        INSERT INTO inventory_warehouses (tenant_id, warehouse_code, name, address) VALUES
        ('550e8400-e29b-41d4-a716-446655440000', 'MAIN', 'Hauptlager', '{"street": "Musterstraße 1", "city": "Musterstadt", "postal_code": "12345", "country": "DE"}');

        INSERT INTO inventory_articles (tenant_id, article_number, name, unit, category, sales_price, minimum_stock) VALUES
        ('550e8400-e29b-41d4-a716-446655440000', 'ART001', 'VALEO Produkt A', 'pcs', 'Elektronik', 99.99, 10),
        ('550e8400-e29b-41d4-a716-446655440000', 'ART002', 'VALEO Produkt B', 'pcs', 'Mechanik', 149.99, 5);
        """

        cursor.executescript(sample_data_sql)
        print("Successfully inserted sample data")

        # Test queries
        cursor.execute("SELECT COUNT(*) FROM shared_tenants")
        tenant_count = cursor.fetchone()[0]
        print(f"Tenants in database: {tenant_count}")

        cursor.execute("SELECT COUNT(*) FROM erp_chart_of_accounts")
        accounts_count = cursor.fetchone()[0]
        print(f"Chart of accounts entries: {accounts_count}")

        cursor.execute("SELECT COUNT(*) FROM inventory_articles")
        articles_count = cursor.fetchone()[0]
        print(f"Articles in inventory: {articles_count}")

        # Commit changes
        conn.commit()
        print("Database setup completed successfully!")

        # Show database info
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print(f"\nCreated tables: {[table[0] for table in tables]}")

    except Exception as e:
        print(f"Error setting up database: {e}")
        if conn:
            conn.rollback()
        return False

    finally:
        if conn:
            conn.close()

    return True

if __name__ == "__main__":
    print("VALEO-NeuroERP SQLite Database Setup Test")
    print("=" * 50)

    success = test_sqlite_database()

    if success:
        print("\n✅ Database setup test PASSED")
        print("The SQLite database is ready for development!")
    else:
        print("\n❌ Database setup test FAILED")
        print("Please check the error messages above.")