"""
Chart of Accounts management endpoints
"""

from fastapi import APIRouter, HTTPException
import sqlite3

router = APIRouter()


@router.get("/")
async def get_chart_of_accounts():
    """Get all accounts"""
    try:
        conn = sqlite3.connect("valeo_neuro_erp.db")
        cursor = conn.cursor()

        cursor.execute("SELECT id, account_number, account_name, account_type, category, is_active FROM erp_chart_of_accounts")
        accounts = cursor.fetchall()

        result = []
        for account in accounts:
            result.append({
                "id": account[0],
                "account_number": account[1],
                "account_name": account[2],
                "account_type": account[3],
                "category": account[4],
                "is_active": bool(account[5])
            })

        conn.close()
        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.get("/{account_id}")
async def get_account(account_id: str):
    """Get account by ID"""
    try:
        conn = sqlite3.connect("valeo_neuro_erp.db")
        cursor = conn.cursor()

        cursor.execute("SELECT id, account_number, account_name, account_type, category, is_active FROM erp_chart_of_accounts WHERE id = ?", (account_id,))
        account = cursor.fetchone()

        conn.close()

        if not account:
            raise HTTPException(status_code=404, detail="Account not found")

        return {
            "id": account[0],
            "account_number": account[1],
            "account_name": account[2],
            "account_type": account[3],
            "category": account[4],
            "is_active": bool(account[5])
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")