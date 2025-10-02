"""
Warehouse management endpoints
"""

from fastapi import APIRouter, HTTPException
import sqlite3

router = APIRouter()


@router.get("/")
async def get_warehouses():
    """Get all warehouses"""
    try:
        conn = sqlite3.connect("valeo_neuro_erp.db")
        cursor = conn.cursor()

        cursor.execute("SELECT id, warehouse_code, name, address, is_active FROM inventory_warehouses")
        warehouses = cursor.fetchall()

        result = []
        for warehouse in warehouses:
            result.append({
                "id": warehouse[0],
                "warehouse_code": warehouse[1],
                "name": warehouse[2],
                "address": warehouse[3],
                "is_active": bool(warehouse[4])
            })

        conn.close()
        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.get("/{warehouse_id}")
async def get_warehouse(warehouse_id: str):
    """Get warehouse by ID"""
    try:
        conn = sqlite3.connect("valeo_neuro_erp.db")
        cursor = conn.cursor()

        cursor.execute("SELECT id, warehouse_code, name, address, is_active FROM inventory_warehouses WHERE id = ?", (warehouse_id,))
        warehouse = cursor.fetchone()

        conn.close()

        if not warehouse:
            raise HTTPException(status_code=404, detail="Warehouse not found")

        return {
            "id": warehouse[0],
            "warehouse_code": warehouse[1],
            "name": warehouse[2],
            "address": warehouse[3],
            "is_active": bool(warehouse[4])
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")