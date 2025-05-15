# Actual Finance MCP Server

This is a Model Context Protocol (MCP) server for Actual Finance, allowing LLM applications to interact with Actual Finance data and functionality.

## Overview

The Actual Finance MCP Server provides:

- Access to financial data through resources (accounts, transactions, categories, budgets)
- Financial management functionality through tools (create/update/delete accounts, transactions, categories)
- Budget management capabilities
- Predefined prompts for common financial analysis tasks

## Setup

1. Install dependencies:
   ```bash
   npm install
   ```

2. Configure environment variables (optional):
   ```bash
   export ACTUAL_SERVER_URL=http://localhost:5006
   export ACTUAL_PASSWORD=your_password
   ```

3. Run the server:
   ```bash
   node server.js
   ```

## Resources

The server exposes the following resources:

| Resource | URI | Description |
|----------|-----|-------------|
| Accounts | `accounts://list` | List all accounts |
| Account Details | `accounts://{accountId}` | Get details for a specific account |
| Categories | `categories://list` | List all categories |
| Category Groups | `category-groups://list` | List all category groups |
| Transactions | `transactions://{accountId}/{startDate}/{endDate}` | Get transactions for an account within a date range |
| Budget Months | `budget-months://list` | List all budget months |
| Budget Month Details | `budget-month://{month}` | Get details for a specific budget month |
| Payees | `payees://list` | List all payees |

## Tools

The server provides the following tools:

### Query Tool
- `runQuery`: Run an ActualQL query

### Account Management
- `createAccount`: Create a new account
- `updateAccount`: Update an existing account
- `closeAccount`: Close an account
- `deleteAccount`: Delete an account

### Transaction Management
- `addTransactions`: Add multiple transactions
- `importTransactions`: Import transactions with reconciliation
- `updateTransaction`: Update a transaction
- `deleteTransaction`: Delete a transaction

### Category Management
- `createCategory`: Create a new category
- `updateCategory`: Update an existing category
- `deleteCategory`: Delete a category

### Budget Management
- `setBudgetAmount`: Set a budget amount for a category
- `setBudgetCarryover`: Enable/disable budget carryover for a category

## Prompts

The server includes the following predefined prompts:

- `budget-analysis`: Analyze budget for a specific month
- `transaction-summary`: Summarize transactions for an account within a date range
- `financial-insights`: Provide general financial insights and recommendations

## Examples

### Using Resources

To get a list of all accounts:
```
GET accounts://list
```

To get transactions for an account:
```
GET transactions://account123/2023-01-01/2023-01-31
```

### Using Tools

To create a new account:
```json
{
  "name": "Checking Account",
  "type": "checking",
  "offBudget": false,
  "initialBalance": 10000
}
```

To add transactions:
```json
{
  "accountId": "account123",
  "transactions": [
    {
      "date": "2023-01-15",
      "amount": 1250,
      "payee_name": "Grocery Store",
      "notes": "Weekly groceries"
    }
  ]
}
```

### Using Prompts

To analyze a budget:
```json
{
  "month": "2023-01"
}
```

## ActualQL Examples

The server supports ActualQL queries through the `runQuery` tool. Here are some examples:

```javascript
// Get all transactions
q('transactions').select('*')

// Get transactions in a specific category
q('transactions')
  .filter({
    'category.name': 'Food'
  })
  .select('*')

// Get total spending by category
q('transactions')
  .groupBy('category.name')
  .select([
    'category.name',
    { $sum: 'amount' }
  ])
```

## License

This project is licensed under the MIT License.
