# Actual MCP Tools and Resources

This document provides a comprehensive reference of Actual's Model Context Protocol (MCP) tools and resources, along with examples of their usage and observations about their functionality.

## Table of Contents

- [Summary of Findings](#summary-of-findings)
- [Resources](#resources)
  - [accounts://list](#accountslist)
  - [accounts://{accountId}](#accountsaccountid)
  - [categories://list](#categorieslist)
  - [category-groups://list](#category-groupslist)
  - [budget-months://list](#budget-monthslist)
  - [budget-month://{month}](#budget-monthmonth)
  - [transactions://{accountId}/{startDate}/{endDate}](#transactionsaccountidstartdateenddate)
  - [payees://list](#payeeslist)
- [Tools](#tools)
  - [createAccount](#createaccount)
  - [updateAccount](#updateaccount)
  - [addTransactions](#addtransactions)
  - [updateTransaction](#updatetransaction)
  - [createCategory](#createcategory)
  - [setBudgetAmount](#setbudgetamount)
  - [setBudgetCarryover](#setbudgetcarryover)
  - [runQuery](#runquery)

## Summary of Findings

| Tool/Resource | Status | Notes |
|---------------|--------|-------|
| accounts://list | ✅ Working | Reliably returns all accounts |
| accounts://{accountId} | ✅ Working | Correctly returns account details with balance |
| categories://list | ✅ Working | Returns complete category list |
| category-groups://list | ✅ Working | Returns category groups with nested categories |
| budget-months://list | ✅ Working | Returns all budget months |
| budget-month://{month} | ⚠️ Partial | Returns budget structure but "spent" amounts not updated immediately |
| transactions://{accountId}/{startDate}/{endDate} | ✅ Working | Returns all transactions within date range |
| payees://list | ✅ Working | Returns all payees |
| createAccount | ✅ Working | Successfully creates accounts with initial balance |
| updateAccount | ❓ Untested | Not fully tested in our session |
| addTransactions | ⚠️ Limited | Works but limited to 2 transactions per request |
| updateTransaction | ✅ Working | Updates transaction properties but may need refresh to see in budget |
| createCategory | ✅ Working | Successfully creates new categories |
| setBudgetAmount | ✅ Working | Sets budget amounts correctly |
| setBudgetCarryover | ✅ Working | Successfully enables/disables carryover |
| runQuery | ❌ Issues | Syntax unclear, encountered errors with basic queries |

## Resources

### accounts://list

Returns a list of all accounts.

**Example Response:**
```json
[
  {
    "id": "2e3b6c8c-a003-44a9-8237-ab42dff50039",
    "name": "HDFC",
    "offbudget": false,
    "closed": false
  },
  {
    "id": "cd2a34b6-4b44-47e9-9cb2-25f1f3697d10",
    "name": "ICICI Savings",
    "offbudget": false,
    "closed": false
  }
]
```

**Observations:**
- This resource works reliably, returning all accounts in the system
- Response includes basic account information but not balances
- Fast response time

### accounts://{accountId}

Returns details for a specific account.

**Example (accounts://2e3b6c8c-a003-44a9-8237-ab42dff50039):**
```json
{
  "id": "2e3b6c8c-a003-44a9-8237-ab42dff50039",
  "name": "HDFC",
  "offbudget": false,
  "closed": false,
  "balance": 600000
}
```

**Observations:**
- Works as expected, returning detailed account information
- Includes the current balance (in smallest currency unit)
- Account type (checking, savings, etc.) is not returned in the response

### categories://list

Returns a list of all categories.

**Example Response:**
```json
[
  {
    "id": "541836f1-e756-4473-a5d0-6c1d3f06c7fa",
    "name": "Food",
    "is_income": false,
    "hidden": false,
    "group_id": "fc3825fd-b982-4b72-b768-5b30844cf832"
  },
  {
    "id": "af375fd4-d759-46b3-bffe-74a856151d57",
    "name": "General",
    "is_income": false,
    "hidden": false,
    "group_id": "fc3825fd-b982-4b72-b768-5b30844cf832"
  },
  {
    "id": "7f887917-27d2-4f1c-8fec-97fac8ff510e",
    "name": "Entertainment",
    "is_income": false,
    "hidden": false,
    "group_id": "fc3825fd-b982-4b72-b768-5b30844cf832"
  },
  // Additional categories...
]
```

**Observations:**
- Returns complete list of categories with their properties
- Includes both system and user-created categories
- Contains group_id reference but not the complete group information

### category-groups://list

Returns a list of all category groups with their associated categories.

**Example Response:**
```json
[
  {
    "id": "fc3825fd-b982-4b72-b768-5b30844cf832",
    "name": "Usual Expenses",
    "is_income": false,
    "hidden": false,
    "categories": [
      {
        "id": "541836f1-e756-4473-a5d0-6c1d3f06c7fa",
        "name": "Food",
        "is_income": false,
        "hidden": false,
        "group_id": "fc3825fd-b982-4b72-b768-5b30844cf832"
      },
      // Additional categories...
    ]
  },
  // Additional groups...
]
```

**Observations:**
- Provides a hierarchical view of category groups and their categories
- More useful than categories://list for understanding the category structure
- Includes the same category properties as categories://list

### budget-months://list

Returns a list of all budget months.

**Example Response:**
```json
[
  "2025-02",
  "2025-03",
  "2025-04",
  "2025-05",
  "2025-06",
  "2025-07",
  "2025-08",
  "2025-09",
  "2025-10",
  "2025-11",
  "2025-12",
  "2026-01",
  "2026-02",
  "2026-03",
  "2026-04"
]
```

**Observations:**
- Returns all budget months in a simple string array
- Includes both past and future months
- Format is consistently "YYYY-MM"

### budget-month://{month}

Returns budget details for a specific month.

**Example (budget-month://2025-05):**
```json
{
  "month": "2025-05",
  "incomeAvailable": 1600000,
  "lastMonthOverspent": 0,
  "forNextMonth": 0,
  "totalBudgeted": -50000,
  "toBudget": 1550000,
  "fromLastMonth": 0,
  "totalIncome": 1600000,
  "totalSpent": 0,
  "totalBalance": 50000,
  "categoryGroups": [
    {
      "id": "fc3825fd-b982-4b72-b768-5b30844cf832",
      "name": "Usual Expenses",
      "is_income": false,
      "hidden": false,
      "categories": [
        {
          "id": "7f887917-27d2-4f1c-8fec-97fac8ff510e",
          "name": "Entertainment",
          "is_income": false,
          "hidden": false,
          "group_id": "fc3825fd-b982-4b72-b768-5b30844cf832",
          "budgeted": 50000,
          "spent": 0,
          "balance": 50000,
          "carryover": true
        },
        // Additional categories...
      ],
      "budgeted": 50000,
      "spent": 0,
      "balance": 50000
    },
    // Additional groups...
  ]
}
```

**Observations:**
- Returns comprehensive budget information for the specified month
- Categorization of transactions may not be immediately reflected in "spent" amounts
- Contains nested structures with category groups and their categories
- Reflects budget amount changes and carryover settings accurately
- Income from all accounts is aggregated in the response

### transactions://{accountId}/{startDate}/{endDate}

Returns transactions for a specific account within a date range.

**Example (transactions://2e3b6c8c-a003-44a9-8237-ab42dff50039/2025-05-01/2025-05-15):**
```json
[
  {
    "id": "ab19923e-97a5-499d-a512-f23c1c5aecd7",
    "is_parent": false,
    "is_child": false,
    "parent_id": null,
    "account": "2e3b6c8c-a003-44a9-8237-ab42dff50039",
    "category": "506e8d9d-7ed0-4397-84e4-07a9185dc6b2",
    "amount": 600000,
    "payee": "5f4ad542-74ee-4045-aba3-9cb3addfe3aa",
    "notes": null,
    "date": "2025-05-15",
    "imported_id": null,
    "error": null,
    "imported_payee": null,
    "starting_balance_flag": true,
    "transfer_id": null,
    "sort_order": 1747299088836,
    "cleared": true,
    "reconciled": false,
    "tombstone": false,
    "schedule": null,
    "raw_synced_data": null,
    "subtransactions": []
  },
  // Additional transactions...
]
```

**Observations:**
- Successfully returns transactions within the specified date range
- Includes detailed transaction information including category assignments
- Very comprehensive data structure with many fields
- Contains IDs for related entities (account, category, payee)
- Date range parameters work as expected

### payees://list

Returns a list of all payees.

**Example Response:**
```json
[
  {
    "id": "4b288c2f-3a11-435f-8afe-74cde9bf6bb1",
    "name": "ABDUL BILAL",
    "transfer_acct": null
  },
  {
    "id": "cac01ddc-07de-40ee-95b5-7c3ecf4f51bc",
    "name": "ANANDA M U",
    "transfer_acct": null
  },
  // Additional payees...
]
```

**Observations:**
- Returns all payees in the system, including those created during transaction import
- Special transfer payees have the transfer_acct field populated with account ID
- Payee IDs are needed when updating transactions

## Tools

### createAccount

Creates a new account.

**Example Input:**
```json
{
  "name": "ICICI Savings",
  "type": "savings",
  "offBudget": false,
  "initialBalance": 1000000
}
```

**Example Response:**
```
Account created successfully with ID: cd2a34b6-4b44-47e9-9cb2-25f1f3697d10
```

**Observations:**
- Works reliably for creating new accounts
- Initial balance must be specified in the smallest currency unit (paise/cents)
- Account type must be one of the supported types (checking, savings, credit, etc.)
- The created account is immediately available for use
- Creates a starting balance transaction automatically

### updateAccount

Updates an existing account's properties.

**Example Input:**
```json
{
  "id": "2e3b6c8c-a003-44a9-8237-ab42dff50039",
  "name": "HDFC Checking",
  "type": "checking"
}
```

**Observations:**
- Not thoroughly tested in our session
- Appears to require the account ID and the fields to update
- Based on the API design, likely works as expected

### addTransactions

Adds transactions to an account.

**Example Input:**
```json
{
  "accountId": "2e3b6c8c-a003-44a9-8237-ab42dff50039",
  "transactions": [
    {
      "date": "2025-05-02",
      "amount": 300,
      "payee_name": "NPCI BHIM-BHIMCASHBACK",
      "notes": "UPI-NPCI BHIM-BHIMCASHBACK@HDFCBANK-HDFC0MERUPI-100477886452-BHIMCASHBACK",
      "cleared": true
    },
    {
      "date": "2025-05-03",
      "amount": -1159400,
      "payee_name": "CRED-PL.IDFC",
      "notes": "UPI-CRED-PL.IDFC@AXISB-UTIB0000114-548901238438-PAYMENT ON CRED",
      "cleared": true
    }
    // Additional transactions...
  ],
  "runTransfers": false,
  "learnCategories": true
}
```

**Example Response:**
```
Added 2 transactions successfully. Transaction IDs: "ok"
```

**Observations:**
- Works but appears to have a limit of processing only 2 transactions per request
- When attempting to add more than 2 transactions, only 2 get processed
- Successfully creates payees automatically from payee_name field
- Positive amounts are treated as income/deposits, negative as expenses/withdrawals
- Date must be in YYYY-MM-DD format

### updateTransaction

Updates a transaction's properties.

**Example Input:**
```json
{
  "id": "b2205048-c69d-4403-b2b0-22510e7d8247",
  "fields": {
    "category": "7f887917-27d2-4f1c-8fec-97fac8ff510e"
  }
}
```

**Example Response:**
```
Transaction b2205048-c69d-4403-b2b0-22510e7d8247 updated successfully
```

**Observations:**
- Successfully updates transaction properties
- The "fields" parameter needs to contain only the properties to update
- Transaction categorization changes don't immediately reflect in budget reports
- Need to use proper IDs for both transaction and category

### createCategory

Creates a new category.

**Example Input:**
```json
{
  "name": "Entertainment",
  "group_id": "fc3825fd-b982-4b72-b768-5b30844cf832",
  "is_income": false
}
```

**Example Response:**
```
Category created successfully with ID: 7f887917-27d2-4f1c-8fec-97fac8ff510e
```

**Observations:**
- Works reliably for creating new categories
- Requires a valid group_id from an existing category group
- The is_income flag determines whether it's a spending or income category
- New categories are immediately available for use in budgeting and transaction categorization

### setBudgetAmount

Sets a budget amount for a category in a specific month.

**Example Input:**
```json
{
  "month": "2025-05",
  "categoryId": "7f887917-27d2-4f1c-8fec-97fac8ff510e",
  "amount": 50000
}
```

**Example Response:**
```
Budget amount for category 7f887917-27d2-4f1c-8fec-97fac8ff510e in 2025-05 set to 50000 cents
```

**Observations:**
- Successfully allocates budget amount to the specified category
- Month format must be YYYY-MM
- Amount must be in smallest currency unit (paise/cents)
- Changes are immediately reflected in the budget

### setBudgetCarryover

Enables or disables budget carryover for a category in a specific month.

**Example Input:**
```json
{
  "month": "2025-05",
  "categoryId": "7f887917-27d2-4f1c-8fec-97fac8ff510e",
  "flag": true
}
```

**Example Response:**
```
Budget carryover for category 7f887917-27d2-4f1c-8fec-97fac8ff510e in 2025-05 enabled
```

**Observations:**
- Successfully enables or disables budget carryover for the specified category
- Changes are immediately reflected in the budget
- When enabled, unspent budget rolls over to the next month

### runQuery

Runs an ActualQL query.

**Example Input:**
```json
{
  "query": "select * from transactions WHERE id = 'b2205048-c69d-4403-b2b0-22510e7d8247'"
}
```

**Example Response:**
```
Error:
Error running query: Unexpected identifier 'transactions'
```

**Observations:**
- We encountered issues with the ActualQL syntax
- Documentation for the correct query syntax appears to be needed
- Simple SQL-like queries resulted in syntax errors
- May require deeper understanding of Actual's internal query language

## Important Notes

1. All monetary amounts are stored in the smallest currency unit (cents/paise).
   - For example, ₹500 is represented as `50000`.

2. IDs are used to reference accounts, categories, transactions, and payees.
   - Always use the correct ID when updating records.

3. Date formats follow the ISO standard: `YYYY-MM-DD`.

4. Most operations return a success message along with relevant IDs.

5. Budget carryover allows unspent budget to roll over to the next month.

6. Connection Issues:
   - The MCP server can occasionally disconnect during long sessions
   - When disconnection occurs, you'll need to restart the server
   - All previously saved data persists after reconnection

7. Transaction Processing:
   - The addTransactions tool appears to process only 2 transactions at a time
   - For bulk importing, batch transactions in groups of 2
   - Categorized transactions may not immediately reflect in budget calculations
