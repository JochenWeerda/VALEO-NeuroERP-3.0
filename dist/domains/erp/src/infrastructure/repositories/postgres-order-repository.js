"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.PostgresOrderRepository = void 0;
const node_crypto_1 = require("node:crypto");
const branded_types_1 = require("../../../../../packages/data-models/src/branded-types");
const postgres_1 = require("../../../../../packages/utilities/src/postgres");
function mapOrderItem(row) {
    return {
        id: row.id,
        articleNumber: row.article_number,
        description: row.description,
        quantity: Number(row.quantity),
        unit: row.unit,
        unitPrice: Number(row.unit_price),
        discount: Number(row.discount),
        netPrice: Number(row.net_price),
        createdAt: new Date(row.created_at),
        updatedAt: new Date(row.updated_at),
    };
}
function mapOrder(row) {
    const rawItems = row.items ?? [];
    const parsedItems = Array.isArray(rawItems)
        ? rawItems
        : JSON.parse(String(rawItems || '[]'));
    return {
        id: (0, branded_types_1.brandValue)(row.id, 'OrderId'),
        orderNumber: row.order_number,
        customerNumber: row.customer_number,
        debtorNumber: row.debtor_number,
        contactPerson: row.contact_person,
        documentType: row.document_type,
        status: row.status,
        documentDate: new Date(row.document_date),
        currency: row.currency,
        netAmount: Number(row.net_amount),
        vatAmount: Number(row.vat_amount),
        totalAmount: Number(row.total_amount),
        notes: row.notes ?? undefined,
        items: parsedItems.map(mapOrderItem),
        createdAt: new Date(row.created_at),
        updatedAt: new Date(row.updated_at),
    };
}
class PostgresOrderRepository {
    constructor(options) {
        this.connectionString = options.connectionString;
        this.poolName = options.poolName ?? 'erp';
        (0, postgres_1.getPostgresPool)({ connectionString: this.connectionString, name: this.poolName });
    }
    async list(filters = {}) {
        const clauses = [];
        const params = [];
        if (filters.status) {
            params.push(filters.status);
            clauses.push('o.status = $' + params.length);
        }
        if (filters.documentType) {
            params.push(filters.documentType);
            clauses.push('o.document_type = $' + params.length);
        }
        if (filters.customerNumber) {
            params.push(filters.customerNumber);
            clauses.push('o.customer_number = $' + params.length);
        }
        if (filters.debtorNumber) {
            params.push(filters.debtorNumber);
            clauses.push('o.debtor_number = $' + params.length);
        }
        if (filters.from) {
            params.push(filters.from);
            clauses.push('o.document_date >= $' + params.length);
        }
        if (filters.to) {
            params.push(filters.to);
            clauses.push('o.document_date <= $' + params.length);
        }
        const limit = filters.limit ?? 50;
        const offset = filters.offset ?? 0;
        params.push(limit);
        params.push(offset);
        const whereSegment = clauses.length ? ' WHERE ' + clauses.join(' AND ') : '';
        const limitIndex = params.length - 1;
        const offsetIndex = params.length;
        const sql = 'SELECT o.id,\n' +
            '       o.order_number,\n' +
            '       o.customer_number,\n' +
            '       o.debtor_number,\n' +
            '       o.contact_person,\n' +
            '       o.document_type,\n' +
            '       o.status,\n' +
            '       o.document_date,\n' +
            '       o.currency,\n' +
            '       o.net_amount,\n' +
            '       o.vat_amount,\n' +
            '       o.total_amount,\n' +
            '       o.notes,\n' +
            '       o.created_at,\n' +
            '       o.updated_at,\n' +
            '       COALESCE(\n' +
            '         json_agg(\n' +
            '           json_build_object(\n' +
            "             'id', p.id,\n" +
            "             'article_number', p.article_number,\n" +
            "             'description', p.description,\n" +
            "             'quantity', p.quantity,\n" +
            "             'unit', p.unit,\n" +
            "             'unit_price', p.unit_price,\n" +
            "             'discount', p.discount,\n" +
            "             'net_price', p.net_price,\n" +
            "             'created_at', p.created_at,\n" +
            "             'updated_at', p.updated_at\n" +
            '           )\n' +
            '         ) FILTER (WHERE p.id IS NOT NULL),\n' +
            "         '[]'\n" +
            '       ) AS items\n' +
            '  FROM erp.orders o\n' +
            '  LEFT JOIN erp.order_positions p ON p.order_id = o.id\n' +
            (whereSegment ? whereSegment + '\n' : '') +
            ' GROUP BY o.id\n' +
            ' ORDER BY o.document_date DESC, o.order_number DESC\n' +
            ' LIMIT $' + limitIndex + '\n' +
            ' OFFSET $' + offsetIndex;
        const pool = (0, postgres_1.getPostgresPool)({ connectionString: this.connectionString, name: this.poolName });
        const result = await pool.query(sql, params);
        return result.rows.map(mapOrder);
    }
    async findById(id) {
        const sql = 'SELECT o.id,\n' +
            '       o.order_number,\n' +
            '       o.customer_number,\n' +
            '       o.debtor_number,\n' +
            '       o.contact_person,\n' +
            '       o.document_type,\n' +
            '       o.status,\n' +
            '       o.document_date,\n' +
            '       o.currency,\n' +
            '       o.net_amount,\n' +
            '       o.vat_amount,\n' +
            '       o.total_amount,\n' +
            '       o.notes,\n' +
            '       o.created_at,\n' +
            '       o.updated_at,\n' +
            '       COALESCE(\n' +
            '         json_agg(\n' +
            '           json_build_object(\n' +
            "             'id', p.id,\n" +
            "             'article_number', p.article_number,\n" +
            "             'description', p.description,\n" +
            "             'quantity', p.quantity,\n" +
            "             'unit', p.unit,\n" +
            "             'unit_price', p.unit_price,\n" +
            "             'discount', p.discount,\n" +
            "             'net_price', p.net_price,\n" +
            "             'created_at', p.created_at,\n" +
            "             'updated_at', p.updated_at\n" +
            '           )\n' +
            '         ) FILTER (WHERE p.id IS NOT NULL),\n' +
            "         '[]'\n" +
            '       ) AS items\n' +
            '  FROM erp.orders o\n' +
            '  LEFT JOIN erp.order_positions p ON p.order_id = o.id\n' +
            ' WHERE o.id = \n' +
            ' GROUP BY o.id\n' +
            ' LIMIT 1';
        const pool = (0, postgres_1.getPostgresPool)({ connectionString: this.connectionString, name: this.poolName });
        const result = await pool.query(sql, [id]);
        if (!result.rowCount) {
            return null;
        }
        return mapOrder(result.rows[0]);
    }
    async create(order) {
        const pool = (0, postgres_1.getPostgresPool)({ connectionString: this.connectionString, name: this.poolName });
        await pool.query('BEGIN');
        try {
            const insertOrderSql = 'INSERT INTO erp.orders (' +
                'id, order_number, customer_number, debtor_number, contact_person, document_type, status, document_date, currency, net_amount, vat_amount, total_amount, notes' +
                ') VALUES (' +
                ', , , , , , , , , 0, 1, 2, 3' +
                ') RETURNING id';
            const orderId = (0, node_crypto_1.randomUUID)();
            await pool.query(insertOrderSql, [
                orderId,
                order.orderNumber,
                order.customerNumber,
                order.debtorNumber,
                order.contactPerson,
                order.documentType,
                order.status,
                order.documentDate,
                order.currency,
                order.netAmount,
                order.vatAmount,
                order.totalAmount,
                order.notes ?? null,
            ]);
            const insertItemSql = 'INSERT INTO erp.order_positions (' +
                'id, order_id, article_number, description, quantity, unit, unit_price, discount, net_price' +
                ') VALUES (' +
                ', , , , , , , , ' +
                ')';
            for (const item of order.items) {
                await pool.query(insertItemSql, [
                    (0, node_crypto_1.randomUUID)(),
                    orderId,
                    item.articleNumber,
                    item.description,
                    item.quantity,
                    item.unit,
                    item.unitPrice,
                    item.discount,
                    item.netPrice,
                ]);
            }
            await pool.query('COMMIT');
            return (await this.findById((0, branded_types_1.brandValue)(orderId, 'OrderId')));
        }
        catch (error) {
            await pool.query('ROLLBACK');
            throw error;
        }
    }
    async updateStatus(id, status) {
        const sql = 'UPDATE erp.orders SET status =  WHERE id =  RETURNING id';
        const pool = (0, postgres_1.getPostgresPool)({ connectionString: this.connectionString, name: this.poolName });
        const result = await pool.query(sql, [id, status]);
        if (!result.rowCount) {
            throw new Error('Order ' + String(id) + ' not found');
        }
        return (await this.findById((0, branded_types_1.brandValue)(result.rows[0].id, 'OrderId')));
    }
    async delete(id) {
        const pool = (0, postgres_1.getPostgresPool)({ connectionString: this.connectionString, name: this.poolName });
        await pool.query('DELETE FROM erp.orders WHERE id = ', [id]);
    }
}
exports.PostgresOrderRepository = PostgresOrderRepository;
