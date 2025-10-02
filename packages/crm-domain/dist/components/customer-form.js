"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || (function () {
    var ownKeys = function(o) {
        ownKeys = Object.getOwnPropertyNames || function (o) {
            var ar = [];
            for (var k in o) if (Object.prototype.hasOwnProperty.call(o, k)) ar[ar.length] = k;
            return ar;
        };
        return ownKeys(o);
    };
    return function (mod) {
        if (mod && mod.__esModule) return mod;
        var result = {};
        if (mod != null) for (var k = ownKeys(mod), i = 0; i < k.length; i++) if (k[i] !== "default") __createBinding(result, mod, k[i]);
        __setModuleDefault(result, mod);
        return result;
    };
})();
Object.defineProperty(exports, "__esModule", { value: true });
exports.CustomerList = void 0;
// domains/crm/src/components/customer-list.tsx
const react_1 = __importStar(require("react"));
const antd_1 = require("antd");
const icons_1 = require("@ant-design/icons");
const smart_import_1 = require("@packages/utilities/smart-import");
const { Title } = antd_1.Typography;
const { Search } = antd_1.Input;
const { Option } = antd_1.Select;
const CustomerList = () => {
    const [customers, setCustomers] = (0, react_1.useState)([]);
    const [loading, setLoading] = (0, react_1.useState)(false);
    const [searchText, setSearchText] = (0, react_1.useState)('');
    const [statusFilter, setStatusFilter] = (0, react_1.useState)('all');
    const smartImport = (0, smart_import_1.useSmartImport)();
    (0, react_1.useEffect)(() => {
        loadCustomers();
    }, [statusFilter]);
    const loadCustomers = async () => {
        setLoading(true);
        try {
            const filters = statusFilter !== 'all' ? { status: statusFilter } : {};
            const customerData = await smartImport.import('@crm/services/crm-domain-service', '');
            const result = await customerData.getCustomers(filters);
            setCustomers(result);
        }
        catch (error) {
            console.error('Failed to load customers:', error);
        }
        finally {
            setLoading(false);
        }
    };
    const handleSearch = (value) => {
        setSearchText(value);
        // Implement search logic
    };
    const handleStatusFilter = (value) => {
        setStatusFilter(value);
    };
    const columns = [
        {
            title: 'Name',
            dataIndex: 'name',
            key: 'name',
            sorter: (a, b) => a.name.localeCompare(b.name),
        },
        {
            title: 'Email',
            dataIndex: 'email',
            key: 'email',
        },
        {
            title: 'Phone',
            dataIndex: 'phone',
            key: 'phone',
        },
        {
            title: 'Status',
            dataIndex: 'status',
            key: 'status',
            render: (status) => {
                const color = status === 'active' ? 'green' : status === 'inactive' ? 'orange' : 'red';
                return <antd_1.Tag color={color}>{status.toUpperCase()}</antd_1.Tag>;
            },
        },
        {
            title: 'Credit Limit',
            dataIndex: 'creditLimit',
            key: 'creditLimit',
            render: (amount) => `€${amount.toLocaleString()}`,
        },
        {
            title: 'Current Balance',
            dataIndex: 'currentBalance',
            key: 'currentBalance',
            render: (amount) => `€${amount.toLocaleString()}`,
        },
        {
            title: 'Actions',
            key: 'actions',
            render: (_, record) => (<antd_1.Space size="middle">
          <antd_1.Button type="primary" icon={<icons_1.EditOutlined />} size="small" onClick={() => handleEdit(record)}>
            Edit
          </antd_1.Button>
          <antd_1.Button type="primary" danger icon={<icons_1.DeleteOutlined />} size="small" onClick={() => handleDelete(record)}>
            Delete
          </antd_1.Button>
        </antd_1.Space>),
        },
    ];
    const handleEdit = (customer) => {
        // Implement edit logic
        console.log('Edit customer:', customer);
    };
    const handleDelete = (customer) => {
        // Implement delete logic
        console.log('Delete customer:', customer);
    };
    const handleAddCustomer = () => {
        // Implement add customer logic
        console.log('Add new customer');
    };
    return (<antd_1.Card>
      <div style={{ marginBottom: 16 }}>
        <Title level={3}>Customer Management</Title>
        <antd_1.Space style={{ marginBottom: 16 }}>
          <Search placeholder="Search customers..." onSearch={handleSearch} style={{ width: 300 }} prefix={<icons_1.SearchOutlined />}/>
          <antd_1.Select value={statusFilter} onChange={handleStatusFilter} style={{ width: 120 }}>
            <Option value="all">All Status</Option>
            <Option value="active">Active</Option>
            <Option value="inactive">Inactive</Option>
            <Option value="suspended">Suspended</Option>
          </antd_1.Select>
          <antd_1.Button type="primary" icon={<icons_1.PlusOutlined />} onClick={handleAddCustomer}>
            Add Customer
          </antd_1.Button>
        </antd_1.Space>
      </div>
      
      <antd_1.Table columns={columns} dataSource={customers} loading={loading} rowKey="id" pagination={{
            pageSize: 10,
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total, range) => `${range[0]}-${range[1]} of ${total} customers`,
        }}/>
    </antd_1.Card>);
};
exports.CustomerList = CustomerList;
//# sourceMappingURL=customer-form.js.map