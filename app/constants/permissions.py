# This list must be manually populated when endpoints are created.
PERMISSION_GROUPS = [
    {
        "group": "super_admin",
        "name": "Super Admin",
        "description": "Bypasses all permission checks",
        "permissions": [
            {
                "value": "super_admin",
                "label": "Super Admin Access",
                "description": "Unrestricted access to all system features"
            }
        ]
    },
    {
        "group": "user_management",
        "name": "User Management",
        "description": "Manage system users and their roles",
        "permissions": [
            { "value": "*", "label": "All Permissions", "description": "Can perform any action on users" },
            { "value": "user:create", "label": "Create Users", "description": "Register new user accounts" },
            { "value": "user:edit", "label": "Edit Users", "description": "Modify user profiles" },
            { "value": "user:view", "label": "View Users", "description": "See list of users" },
            { "value": "user:view_profile", "label": "View User Profile", "description": "View full profile or audit" },
            { "value": "user:delete", "label": "Delete Users", "description": "Temporarily remove user accounts" },
            { "value": "user:hard_delete", "label": "Permanently Delete Users", "description": "Irreversibly remove accounts" },
            { "value": "user:reset_password", "label": "Reset Passwords", "description": "Reset user passwords" },
            { "value": "user:assign_roles", "label": "Assign Roles", "description": "Manage role assignments" },
            { "value": "user:deactivate", "label": "Deactivate User", "description": "Temporarily disable a user" },
            { "value": "user:activate", "label": "Activate User", "description": "Re-enable a previously disabled user" },
            { "value": "user:invite", "label": "Invite User", "description": "Send invitation email to new user" },
            { "value": "user:resend_invite", "label": "Resend Invite", "description": "Resend pending invitation email" },
            { "value": "user:export", "label": "Export Users", "description": "Export user list to CSV or PDF" },
            { "value": "user:impersonate", "label": "Impersonate User", "description": "Log in as another user for testing or support" },
            { "value": "user:bulk_edit", "label": "Bulk Edit Users", "description": "Modify multiple users at once" },
            { "value": "user:bulk_delete", "label": "Bulk Delete Users", "description": "Delete multiple users at once" },
            { "value": "user:view_activity", "label": "View User Activity", "description": "Access logs of user actions" },
            { "value": "user:manage_sessions", "label": "Manage Sessions", "description": "View or terminate active user sessions" },
            { "value": "user:manage_permissions", "label": "Manage Permissions", "description": "Edit individual user permissions" },
            { "value": "user:view_statistics", "label": "View User Statistics", "description": "Access analytics on user behavior" }
        ]
    },
    {
        "group": "role_management",
        "name": "Role Management",
        "description": "Define and manage roles and their associated permissions",
        "permissions": [
            { "value": "*", "label": "All Role Permissions", "description": "Can perform any action related to roles" },
            { "value": "role:create", "label": "Create Roles", "description": "Create new roles with specific permission sets" },
            { "value": "role:edit", "label": "Edit Roles", "description": "Change role name or update assigned permissions" },
            { "value": "role:view", "label": "View Roles", "description": "List all available roles" },
            { "value": "role:view_detail", "label": "View Role Details", "description": "Inspect role configuration and permission mappings" },
            { "value": "role:delete", "label": "Delete Roles", "description": "Soft delete a role from the system" },
            { "value": "role:hard_delete", "label": "Permanently Delete Roles", "description": "Remove a role and its history completely" },
            { "value": "role:duplicate", "label": "Duplicate Roles", "description": "Create a new role based on an existing one" },
            { "value": "role:export", "label": "Export Roles", "description": "Download all role definitions as CSV or JSON" },
            { "value": "role:audit", "label": "Audit Role Changes", "description": "Review change logs for roles and permission edits" }
        ]
    },
    {
        "group": "branch_management",
        "name": "Branch Management",
        "description": "Manage multiple locations/branches",
        "permissions": [
            {
                "value": "can_manage_branches",
                "label": "Manage Branches",
                "description": "Create, edit and delete branch locations"
            },
            {
                "value": "can_switch_branch",
                "label": "Switch Branches",
                "description": "Change active branch context"
            }
        ]
    },
    {
        "group": "product_inventory",
        "name": "Product & Inventory",
        "description": "Manage products and stock levels",
        "permissions": [
            {
                "value": "can_add_product",
                "label": "Add Products",
                "description": "Create new product entries"
            },
            {
                "value": "can_edit_product",
                "label": "Edit Products",
                "description": "Modify existing product details"
            },
            {
                "value": "can_delete_product",
                "label": "Delete Products",
                "description": "Remove products from catalog"
            },
            {
                "value": "can_view_product",
                "label": "View Products",
                "description": "Browse product catalog"
            },
            {
                "value": "can_adjust_inventory",
                "label": "Adjust Inventory",
                "description": "Update stock quantities"
            },
            {
                "value": "can_view_inventory",
                "label": "View Inventory",
                "description": "Check current stock levels"
            },
            {
                "value": "can_manage_categories",
                "label": "Manage Categories",
                "description": "Organize product categories"
            },
            {
                "value": "can_manage_brands",
                "label": "Manage Brands",
                "description": "Handle brand information"
            },
            {
                "value": "can_manage_warehouses",
                "label": "Manage Warehouses",
                "description": "Configure storage locations"
            }
        ]
    },
    {
        "group": "sales_orders",
        "name": "Sales & Orders",
        "description": "Process customer orders and POS operations",
        "permissions": [
            {
                "value": "can_create_order",
                "label": "Create Orders",
                "description": "Initiate new sales orders"
            },
            {
                "value": "can_edit_order",
                "label": "Edit Orders",
                "description": "Modify pending orders"
            },
            {
                "value": "can_cancel_order",
                "label": "Cancel Orders",
                "description": "Void/Cancel existing orders"
            },
            {
                "value": "can_view_orders",
                "label": "View Orders",
                "description": "Access order history"
            },
            {
                "value": "can_refund_order",
                "label": "Process Refunds",
                "description": "Issue order refunds"
            },
            {
                "value": "can_void_transactions",
                "label": "Void Transactions",
                "description": "Cancel completed transactions"
            },
            {
                "value": "can_process_refunds",
                "label": "Process Refunds",
                "description": "Handle refund requests"
            },
            {
                "value": "can_reprint_receipt",
                "label": "Reprint Receipts",
                "description": "Generate duplicate receipts"
            },
            {
                "value": "can_split_bills",
                "label": "Split Bills",
                "description": "Divide payments across methods"
            },
            {
                "value": "can_apply_discounts",
                "label": "Apply Discounts",
                "description": "Authorize price adjustments"
            },
            {
                "value": "can_manage_pos",
                "label": "Manage POS",
                "description": "Configure point-of-sale settings"
            }
        ]
    },
    {
        "group": "payments",
        "name": "Payments",
        "description": "Handle payment processing",
        "permissions": [
            {
                "value": "can_accept_payment",
                "label": "Accept Payments",
                "description": "Process customer payments"
            },
            {
                "value": "can_view_payments",
                "label": "View Payments",
                "description": "See payment transaction history"
            },
            {
                "value": "can_issue_receipt",
                "label": "Issue Receipts",
                "description": "Generate payment confirmations"
            },
            {
                "value": "can_approve_cashback",
                "label": "Approve Cashback",
                "description": "Authorize cashback offers"
            }
        ]
    },
    {
        "group": "accounting_finance",
        "name": "Accounting & Finance",
        "description": "Financial management and reporting",
        "permissions": [
            {
                "value": "can_view_accounts",
                "label": "View Accounts",
                "description": "Access financial accounts"
            },
            {
                "value": "can_edit_accounts",
                "label": "Edit Accounts",
                "description": "Modify accounting entries"
            },
            {
                "value": "can_approve_expenditures",
                "label": "Approve Expenditures",
                "description": "Authorize expense payments"
            },
            {
                "value": "can_manage_payroll",
                "label": "Manage Payroll",
                "description": "Handle employee compensation"
            },
            {
                "value": "can_view_financial_reports",
                "label": "View Financial Reports",
                "description": "Access profit/loss statements"
            },
            {
                "value": "can_view_payroll_reports",
                "label": "View Payroll Reports",
                "description": "Access compensation analytics"
            }
        ]
    },
    {
        "group": "human_resources",
        "name": "Human Resources",
        "description": "Employee management and attendance",
        "permissions": [
            {
                "value": "can_manage_staff",
                "label": "Manage Staff",
                "description": "Handle employee records"
            },
            {
                "value": "can_view_hr_records",
                "label": "View HR Records",
                "description": "Access personnel files"
            },
            {
                "value": "can_approve_leave",
                "label": "Approve Leave",
                "description": "Authorize time-off requests"
            },
            {
                "value": "can_manage_benefits",
                "label": "Manage Benefits",
                "description": "Administer employee benefits"
            },
            {
                "value": "can_clock_in_out",
                "label": "Clock In/Out",
                "description": "Record work hours"
            },
            {
                "value": "can_view_attendance",
                "label": "View Attendance",
                "description": "Check staff presence records"
            }
        ]
    },
    {
        "group": "customer_management",
        "name": "Customer Management",
        "description": "Customer relationship management",
        "permissions": [
            {
                "value": "can_view_customers",
                "label": "View Customers",
                "description": "Access customer database"
            },
            {
                "value": "can_edit_customer",
                "label": "Edit Customers",
                "description": "Update customer profiles"
            },
            {
                "value": "can_delete_customer",
                "label": "Delete Customers",
                "description": "Remove customer records"
            },
            {
                "value": "can_escalate_issues",
                "label": "Escalate Issues",
                "description": "Raise customer complaints"
            },
            {
                "value": "can_view_customer_feedback",
                "label": "View Feedback",
                "description": "See customer satisfaction data"
            },
            {
                "value": "can_manage_loyalty_program",
                "label": "Manage Loyalty",
                "description": "Administer rewards program"
            }
        ]
    },
    {
        "group": "procurement",
        "name": "Procurement",
        "description": "Supplier and purchasing management",
        "permissions": [
            {
                "value": "can_add_supplier",
                "label": "Add Suppliers",
                "description": "Register new vendors"
            },
            {
                "value": "can_view_suppliers",
                "label": "View Suppliers",
                "description": "Access vendor database"
            },
            {
                "value": "can_make_purchase_request",
                "label": "Create Purchase Requests",
                "description": "Initiate procurement orders"
            },
            {
                "value": "can_approve_purchase_request",
                "label": "Approve Purchases",
                "description": "Authorize procurement spending"
            },
            {
                "value": "can_view_purchase_history",
                "label": "View Purchase History",
                "description": "Access procurement records"
            },
            {
                "value": "can_manage_contracts",
                "label": "Manage Contracts",
                "description": "Handle vendor agreements"
            }
        ]
    },
    {
        "group": "maintenance",
        "name": "Maintenance",
        "description": "Facility and equipment maintenance",
        "permissions": [
            {
                "value": "can_log_maintenance",
                "label": "Log Maintenance",
                "description": "Record maintenance activities"
            },
            {
                "value": "can_view_maintenance_logs",
                "label": "View Maintenance Logs",
                "description": "Access maintenance history"
            },
            {
                "value": "can_request_maintenance_supplies",
                "label": "Request Supplies",
                "description": "Order maintenance materials"
            }
        ]
    },
    {
        "group": "marketing",
        "name": "Marketing",
        "description": "Promotions and business development",
        "permissions": [
            {
                "value": "can_create_campaign",
                "label": "Create Campaigns",
                "description": "Launch marketing initiatives"
            },
            {
                "value": "can_edit_campaign",
                "label": "Edit Campaigns",
                "description": "Modify marketing programs"
            },
            {
                "value": "can_delete_campaign",
                "label": "Delete Campaigns",
                "description": "Remove marketing activities"
            },
            {
                "value": "can_view_leads",
                "label": "View Leads",
                "description": "Access potential customer data"
            },
            {
                "value": "can_manage_discounts",
                "label": "Manage Discounts",
                "description": "Configure promotional pricing"
            }
        ]
    },
    {
        "group": "reports",
        "name": "Reports & Analytics",
        "description": "Data analysis and reporting",
        "permissions": [
            {
                "value": "can_view_sales_reports",
                "label": "View Sales Reports",
                "description": "Access sales performance data"
            },
            {
                "value": "can_view_inventory_reports",
                "label": "View Inventory Reports",
                "description": "Access stock analysis"
            },
            {
                "value": "can_view_audit_logs",
                "label": "View Audit Logs",
                "description": "See system activity records"
            },
            {
                "value": "can_generate_custom_reports",
                "label": "Generate Custom Reports",
                "description": "Create ad-hoc analytics"
            },
            {
                "value": "can_export_reports",
                "label": "Export Reports",
                "description": "Download report data"
            },
            {
                "value": "can_view_sensitive_data",
                "label": "View Sensitive Data",
                "description": "Access restricted information"
            },
            {
                "value": "can_export_audit_logs",
                "label": "Export Audit Logs",
                "description": "Download activity records"
            }
        ]
    },
    {
        "group": "store_kitchen",
        "name": "Store & Kitchen",
        "description": "Retail and food service operations",
        "permissions": [
            {
                "value": "can_manage_store_stock",
                "label": "Manage Store Stock",
                "description": "Handle retail inventory"
            },
            {
                "value": "can_manage_kitchen_orders",
                "label": "Manage Kitchen Orders",
                "description": "Coordinate food preparation"
            },
            {
                "value": "can_update_order_status",
                "label": "Update Order Status",
                "description": "Change preparation stages"
            },
            {
                "value": "can_view_kitchen_analytics",
                "label": "View Kitchen Analytics",
                "description": "Access food service metrics"
            }
        ]
    },
    {
        "group": "system_admin",
        "name": "System Administration",
        "description": "Technical system configuration",
        "permissions": [
            {
                "value": "can_manage_system_settings",
                "label": "Manage System Settings",
                "description": "Configure application parameters"
            },
            {
                "value": "can_backup_data",
                "label": "Backup Data",
                "description": "Create system backups"
            },
            {
                "value": "can_view_logs",
                "label": "View System Logs",
                "description": "Access technical logs"
            },
            {
                "value": "can_manage_api_keys",
                "label": "Manage API Keys",
                "description": "Handle integration credentials"
            },
            {
                "value": "can_access_integrations",
                "label": "Access Integrations",
                "description": "Configure third-party connections"
            },
            {
                "value": "can_export_data",
                "label": "Export Data",
                "description": "Download system data"
            },
            {
                "value": "can_anonymize_data",
                "label": "Anonymize Data",
                "description": "Remove personal identifiers"
            }
        ]
    },
    {
        "group": "notifications",
        "name": "Notifications",
        "description": "Alerts and messaging",
        "permissions": [
            {
                "value": "can_manage_notifications",
                "label": "Manage Notifications",
                "description": "Configure alert systems"
            },
            {
                "value": "can_send_bulk_messages",
                "label": "Send Bulk Messages",
                "description": "Distribute mass communications"
            }
        ]
    },
    {
        "group": "audit_security",
        "name": "Audit & Security",
        "description": "Security and compliance",
        "permissions": [
            {
                "value": "can_view_sensitive_data",
                "label": "View Sensitive Data",
                "description": "Access restricted information"
            },
            {
                "value": "can_export_audit_logs",
                "label": "Export Audit Logs",
                "description": "Download security records"
            }
        ]
    }
]
