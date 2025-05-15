var __awaiter = (this && this.__awaiter) || function (thisArg, _arguments, P, generator) {
    function adopt(value) { return value instanceof P ? value : new P(function (resolve) { resolve(value); }); }
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : adopt(result.value).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};
import { McpServer, ResourceTemplate } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";
import * as actualApi from '@actual-app/api';
import * as fs from 'fs';
import * as path from 'path';
// Initialize Actual API
function initActualApi() {
    return __awaiter(this, void 0, void 0, function* () {
        try {
            const serverURL = process.env.ACTUAL_SERVER_URL || 'http://localhost:5006';
            console.log(`Connecting to Actual API at ${serverURL}...`);
            // Create the actual-data directory if it doesn't exist
            // Use an absolute path to ensure consistency regardless of working directory
            // For ES modules, we need to use import.meta.url instead of __dirname
            const currentFileUrl = import.meta.url;
            const currentFilePath = new URL(currentFileUrl).pathname;
            const currentDir = path.dirname(currentFilePath);
            const dataDir = path.resolve(currentDir, '..', 'actual-data');
            console.log(`Using data directory: ${dataDir}`);
            if (!fs.existsSync(dataDir)) {
                console.log(`Creating data directory: ${dataDir}`);
                fs.mkdirSync(dataDir, { recursive: true });
            }
            // Initialize the API with the server URL, password, and data directory
            yield actualApi.init({
                serverURL: serverURL,
                password: process.env.ACTUAL_PASSWORD || 'password',
                dataDir: dataDir, // Save budget data in the actual-data directory
            });
            console.log('Successfully connected to Actual API');
            // Try to get budgets
            console.log('Fetching available budgets...');
            const budgets = yield actualApi.getBudgets();
            if (budgets && Array.isArray(budgets) && budgets.length > 0) {
                // Get the first budget
                const budget = budgets[0];
                console.log(`Found budget: ${budget.name}`);
                try {
                    // Try different IDs in order of preference
                    const possibleIds = [
                        budget.groupId,
                        budget.cloudFileId,
                        budget.id
                    ].filter(Boolean); // Remove any undefined or null values
                    if (possibleIds.length === 0) {
                        throw new Error('Budget does not have any valid IDs');
                    }
                    let downloaded = false;
                    for (const id of possibleIds) {
                        try {
                            console.log(`Attempting to download budget with ID: ${id}`);
                            yield actualApi.downloadBudget(id);
                            console.log(`Successfully downloaded budget: ${budget.name} with ID: ${id}`);
                            downloaded = true;
                            break;
                        }
                        catch (loadError) {
                            console.log(`Failed to download budget with ID ${id}: ${loadError.message || String(loadError)}`);
                            // Continue to the next ID
                        }
                    }
                    if (!downloaded) {
                        throw new Error('Failed to download budget with any of the available IDs');
                    }
                }
                catch (error) {
                    console.error('Error downloading budget:', error);
                    console.error('Budget details:', JSON.stringify(budget, null, 2));
                    console.error('The MCP server will start, but budget operations may not work correctly.');
                }
            }
            else {
                console.log('No budgets available. You may need to create a budget first.');
                console.log('If you already have budgets, check if they are properly synced to the server.');
                console.log('The MCP server will start, but budget operations may not work correctly.');
            }
        }
        catch (error) {
            console.error('Failed to initialize Actual API:', error);
            console.error('Error details:', error.message || String(error));
            throw error;
        }
    });
}
// Create an MCP server
const server = new McpServer({
    name: "Actual Finance MCP",
    version: "1.0.0"
});
// ==================== RESOURCES ====================
// Accounts resource
server.resource("accounts", "accounts://list", (uri) => __awaiter(void 0, void 0, void 0, function* () {
    try {
        const accounts = yield actualApi.getAccounts();
        return {
            contents: [{
                    uri: uri.href,
                    text: JSON.stringify(accounts, null, 2)
                }]
        };
    }
    catch (error) {
        console.error('Error fetching accounts:', error);
        return {
            contents: [{
                    uri: uri.href,
                    text: `Error fetching accounts: ${error.message || String(error) || String(error)}`
                }]
        };
    }
}));
// Account details resource
server.resource("account", new ResourceTemplate("accounts://{accountId}", { list: undefined }), (uri_1, _a) => __awaiter(void 0, [uri_1, _a], void 0, function* (uri, { accountId }) {
    try {
        const accounts = yield actualApi.getAccounts();
        const account = accounts.find(acc => acc.id === accountId);
        if (!account) {
            return {
                contents: [{
                        uri: uri.href,
                        text: `Account with ID ${accountId} not found`
                    }]
            };
        }
        // Get the account balance
        const balance = yield actualApi.getAccountBalance(accountId);
        return {
            contents: [{
                    uri: uri.href,
                    text: JSON.stringify(Object.assign(Object.assign({}, account), { balance }), null, 2)
                }]
        };
    }
    catch (error) {
        console.error(`Error fetching account ${accountId}:`, error);
        return {
            contents: [{
                    uri: uri.href,
                    text: `Error fetching account: ${error.message || String(error) || String(error)}`
                }]
        };
    }
}));
// Categories resource
server.resource("categories", "categories://list", (uri) => __awaiter(void 0, void 0, void 0, function* () {
    try {
        const categories = yield actualApi.getCategories();
        return {
            contents: [{
                    uri: uri.href,
                    text: JSON.stringify(categories, null, 2)
                }]
        };
    }
    catch (error) {
        console.error('Error fetching categories:', error);
        return {
            contents: [{
                    uri: uri.href,
                    text: `Error fetching categories: ${error.message || String(error)}`
                }]
        };
    }
}));
// Category groups resource
server.resource("categoryGroups", "category-groups://list", (uri) => __awaiter(void 0, void 0, void 0, function* () {
    try {
        const categoryGroups = yield actualApi.getCategoryGroups();
        return {
            contents: [{
                    uri: uri.href,
                    text: JSON.stringify(categoryGroups, null, 2)
                }]
        };
    }
    catch (error) {
        console.error('Error fetching category groups:', error);
        return {
            contents: [{
                    uri: uri.href,
                    text: `Error fetching category groups: ${error.message || String(error)}`
                }]
        };
    }
}));
// Transactions resource
server.resource("transactions", new ResourceTemplate("transactions://{accountId}/{startDate}/{endDate}", { list: undefined }), (uri_1, _a) => __awaiter(void 0, [uri_1, _a], void 0, function* (uri, { accountId, startDate, endDate }) {
    try {
        const transactions = yield actualApi.getTransactions(accountId, startDate, endDate);
        return {
            contents: [{
                    uri: uri.href,
                    text: JSON.stringify(transactions, null, 2)
                }]
        };
    }
    catch (error) {
        console.error(`Error fetching transactions for account ${accountId}:`, error);
        return {
            contents: [{
                    uri: uri.href,
                    text: `Error fetching transactions: ${error.message || String(error)}`
                }]
        };
    }
}));
// Budget months resource
server.resource("budgetMonths", "budget-months://list", (uri) => __awaiter(void 0, void 0, void 0, function* () {
    try {
        const budgetMonths = yield actualApi.getBudgetMonths();
        return {
            contents: [{
                    uri: uri.href,
                    text: JSON.stringify(budgetMonths, null, 2)
                }]
        };
    }
    catch (error) {
        console.error('Error fetching budget months:', error);
        return {
            contents: [{
                    uri: uri.href,
                    text: `Error fetching budget months: ${error.message || String(error)}`
                }]
        };
    }
}));
// Budget month details resource
server.resource("budgetMonth", new ResourceTemplate("budget-month://{month}", { list: undefined }), (uri_1, _a) => __awaiter(void 0, [uri_1, _a], void 0, function* (uri, { month }) {
    try {
        const budgetMonth = yield actualApi.getBudgetMonth(month);
        return {
            contents: [{
                    uri: uri.href,
                    text: JSON.stringify(budgetMonth, null, 2)
                }]
        };
    }
    catch (error) {
        console.error(`Error fetching budget month ${month}:`, error);
        return {
            contents: [{
                    uri: uri.href,
                    text: `Error fetching budget month: ${error.message || String(error)}`
                }]
        };
    }
}));
// Payees resource
server.resource("payees", "payees://list", (uri) => __awaiter(void 0, void 0, void 0, function* () {
    try {
        const payees = yield actualApi.getPayees();
        return {
            contents: [{
                    uri: uri.href,
                    text: JSON.stringify(payees, null, 2)
                }]
        };
    }
    catch (error) {
        console.error('Error fetching payees:', error);
        return {
            contents: [{
                    uri: uri.href,
                    text: `Error fetching payees: ${error.message || String(error)}`
                }]
        };
    }
}));
// ==================== TOOLS ====================
// Run ActualQL query
// server.tool(
//   "runQuery",
//   {
//     query: z.string().describe("ActualQL query string to execute")
//   },
//   async ({ query }) => {
//     try {
//       // Parse the query string to create an ActualQL query
//       // Instead of using eval, we'll use the q function from the API
//       // This is safer and handles the query construction properly
//       const { q } = actualApi;
//       // The query should be a string representation of how to construct a query
//       // For example: "q('transactions').select('*')"
//       // We'll use Function constructor to safely evaluate it with access to the q function
//       const queryConstructor = new Function('q', `return ${query}`);
//       const parsedQuery = queryConstructor(q);
//       const result = await actualApi.runQuery(parsedQuery);
//       return {
//         content: [{
//           type: "text",
//           text: JSON.stringify(result, null, 2)
//         }]
//       };
//     } catch (error: any) {
//       console.error('Error running query:', error);
//       return {
//         content: [{
//           type: "text",
//           text: `Error running query: ${error.message || String(error)}`
//         }],
//         isError: true
//       };
//     }
//   }
// );
// Create account
server.tool("createAccount", {
    name: z.string().describe("Account name"),
    type: z.enum(['checking', 'savings', 'credit', 'investment', 'mortgage', 'debt', 'other']).describe("Account type"),
    offBudget: z.boolean().optional().describe("Whether the account is off-budget"),
    initialBalance: z.number().optional().describe("Initial balance in cents")
}, (_a) => __awaiter(void 0, [_a], void 0, function* ({ name, type, offBudget, initialBalance = 0 }) {
    try {
        const accountId = yield actualApi.createAccount({
            name,
            type,
            offbudget: offBudget
        }, initialBalance);
        return {
            content: [{
                    type: "text",
                    text: `Account created successfully with ID: ${accountId}`
                }]
        };
    }
    catch (error) {
        console.error('Error creating account:', error);
        return {
            content: [{
                    type: "text",
                    text: `Error creating account: ${error.message || String(error)}`
                }],
            isError: true
        };
    }
}));
// Update account
server.tool("updateAccount", {
    id: z.string().describe("Account ID"),
    name: z.string().optional().describe("New account name"),
    type: z.enum(['checking', 'savings', 'credit', 'investment', 'mortgage', 'debt', 'other']).optional().describe("New account type"),
    offBudget: z.boolean().optional().describe("Whether the account is off-budget")
}, (_a) => __awaiter(void 0, [_a], void 0, function* ({ id, name, type, offBudget }) {
    try {
        const fields = {};
        if (name !== undefined)
            fields.name = name;
        if (type !== undefined)
            fields.type = type;
        if (offBudget !== undefined)
            fields.offbudget = offBudget;
        yield actualApi.updateAccount(id, fields);
        return {
            content: [{
                    type: "text",
                    text: `Account ${id} updated successfully`
                }]
        };
    }
    catch (error) {
        console.error('Error updating account:', error);
        return {
            content: [{
                    type: "text",
                    text: `Error updating account: ${error.message || String(error)}`
                }],
            isError: true
        };
    }
}));
// Close account
server.tool("closeAccount", {
    id: z.string().describe("Account ID"),
    transferAccountId: z.string().optional().describe("Account ID to transfer remaining balance to"),
    transferCategoryId: z.string().optional().describe("Category ID for the transfer (required for on-budget to off-budget transfers)")
}, (_a) => __awaiter(void 0, [_a], void 0, function* ({ id, transferAccountId, transferCategoryId }) {
    try {
        yield actualApi.closeAccount(id, transferAccountId, transferCategoryId);
        return {
            content: [{
                    type: "text",
                    text: `Account ${id} closed successfully`
                }]
        };
    }
    catch (error) {
        console.error('Error closing account:', error);
        return {
            content: [{
                    type: "text",
                    text: `Error closing account: ${error.message || String(error)}`
                }],
            isError: true
        };
    }
}));
// Delete account
server.tool("deleteAccount", {
    id: z.string().describe("Account ID to delete")
}, (_a) => __awaiter(void 0, [_a], void 0, function* ({ id }) {
    try {
        yield actualApi.deleteAccount(id);
        return {
            content: [{
                    type: "text",
                    text: `Account ${id} deleted successfully`
                }]
        };
    }
    catch (error) {
        console.error('Error deleting account:', error);
        return {
            content: [{
                    type: "text",
                    text: `Error deleting account: ${error.message || String(error)}`
                }],
            isError: true
        };
    }
}));
// Add transactions
server.tool("addTransactions", {
    accountId: z.string().describe("Account ID"),
    transactions: z.array(z.object({
        date: z.string().describe("Transaction date (YYYY-MM-DD)"),
        amount: z.number().describe("Transaction amount in cents"),
        payee_name: z.string().optional().describe("Payee name"),
        category_id: z.string().optional().describe("Category ID"),
        notes: z.string().optional().describe("Transaction notes"),
        cleared: z.boolean().optional().describe("Whether the transaction is cleared")
    })).describe("Array of transactions to add"),
    runTransfers: z.boolean().optional().describe("Whether to create transfers for transactions with transfer payees"),
    learnCategories: z.boolean().optional().describe("Whether to update rules based on categories")
}, (_a) => __awaiter(void 0, [_a], void 0, function* ({ accountId, transactions, runTransfers = false, learnCategories = false }) {
    try {
        // The API documentation shows that addTransactions takes 2-3 arguments
        // Let's create an options object for the optional parameters
        const options = {};
        if (runTransfers !== undefined)
            options.runTransfers = runTransfers;
        if (learnCategories !== undefined)
            options.learnCategories = learnCategories;
        const transactionIds = yield actualApi.addTransactions(accountId, transactions, options);
        return {
            content: [{
                    type: "text",
                    text: `Added ${transactionIds.length} transactions successfully. Transaction IDs: ${JSON.stringify(transactionIds)}`
                }]
        };
    }
    catch (error) {
        console.error('Error adding transactions:', error);
        return {
            content: [{
                    type: "text",
                    text: `Error adding transactions: ${error.message || String(error)}`
                }],
            isError: true
        };
    }
}));
// Import transactions
server.tool("importTransactions", {
    accountId: z.string().describe("Account ID"),
    transactions: z.array(z.object({
        date: z.string().describe("Transaction date (YYYY-MM-DD)"),
        amount: z.number().describe("Transaction amount in cents"),
        payee_name: z.string().optional().describe("Payee name"),
        category_id: z.string().optional().describe("Category ID"),
        notes: z.string().optional().describe("Transaction notes"),
        imported_id: z.string().optional().describe("Imported ID to avoid duplicates"),
        cleared: z.boolean().optional().describe("Whether the transaction is cleared")
    })).describe("Array of transactions to import")
}, (_a) => __awaiter(void 0, [_a], void 0, function* ({ accountId, transactions }) {
    try {
        const result = yield actualApi.importTransactions(accountId, transactions);
        return {
            content: [{
                    type: "text",
                    text: `Import result: ${JSON.stringify(result, null, 2)}`
                }]
        };
    }
    catch (error) {
        console.error('Error importing transactions:', error);
        return {
            content: [{
                    type: "text",
                    text: `Error importing transactions: ${error.message || String(error)}`
                }],
            isError: true
        };
    }
}));
// Update transaction
server.tool("updateTransaction", {
    id: z.string().describe("Transaction ID"),
    fields: z.object({
        date: z.string().optional().describe("Transaction date (YYYY-MM-DD)"),
        amount: z.number().optional().describe("Transaction amount in cents"),
        payee_id: z.string().optional().describe("Payee ID"),
        category_id: z.string().optional().describe("Category ID"),
        notes: z.string().optional().describe("Transaction notes"),
        cleared: z.boolean().optional().describe("Whether the transaction is cleared")
    }).describe("Fields to update")
}, (_a) => __awaiter(void 0, [_a], void 0, function* ({ id, fields }) {
    try {
        yield actualApi.updateTransaction(id, fields);
        return {
            content: [{
                    type: "text",
                    text: `Transaction ${id} updated successfully`
                }]
        };
    }
    catch (error) {
        console.error('Error updating transaction:', error);
        return {
            content: [{
                    type: "text",
                    text: `Error updating transaction: ${error.message || String(error)}`
                }],
            isError: true
        };
    }
}));
// Delete transaction
server.tool("deleteTransaction", {
    id: z.string().describe("Transaction ID to delete")
}, (_a) => __awaiter(void 0, [_a], void 0, function* ({ id }) {
    try {
        yield actualApi.deleteTransaction(id);
        return {
            content: [{
                    type: "text",
                    text: `Transaction ${id} deleted successfully`
                }]
        };
    }
    catch (error) {
        console.error('Error deleting transaction:', error);
        return {
            content: [{
                    type: "text",
                    text: `Error deleting transaction: ${error.message || String(error)}`
                }],
            isError: true
        };
    }
}));
// Create category
server.tool("createCategory", {
    name: z.string().describe("Category name"),
    group_id: z.string().describe("Category group ID"),
    is_income: z.boolean().optional().describe("Whether this is an income category")
}, (_a) => __awaiter(void 0, [_a], void 0, function* ({ name, group_id, is_income }) {
    try {
        const categoryId = yield actualApi.createCategory({
            name,
            group_id,
            is_income: is_income || false
        });
        return {
            content: [{
                    type: "text",
                    text: `Category created successfully with ID: ${categoryId}`
                }]
        };
    }
    catch (error) {
        console.error('Error creating category:', error);
        return {
            content: [{
                    type: "text",
                    text: `Error creating category: ${error.message || String(error)}`
                }],
            isError: true
        };
    }
}));
// Update category
server.tool("updateCategory", {
    id: z.string().describe("Category ID"),
    name: z.string().optional().describe("New category name"),
    group_id: z.string().optional().describe("New category group ID"),
    is_income: z.boolean().optional().describe("Whether this is an income category")
}, (_a) => __awaiter(void 0, [_a], void 0, function* ({ id, name, group_id, is_income }) {
    try {
        const fields = {};
        if (name !== undefined)
            fields.name = name;
        if (group_id !== undefined)
            fields.group_id = group_id;
        if (is_income !== undefined)
            fields.is_income = is_income;
        yield actualApi.updateCategory(id, fields);
        return {
            content: [{
                    type: "text",
                    text: `Category ${id} updated successfully`
                }]
        };
    }
    catch (error) {
        console.error('Error updating category:', error);
        return {
            content: [{
                    type: "text",
                    text: `Error updating category: ${error.message || String(error)}`
                }],
            isError: true
        };
    }
}));
// Delete category
server.tool("deleteCategory", {
    id: z.string().describe("Category ID to delete")
}, (_a) => __awaiter(void 0, [_a], void 0, function* ({ id }) {
    try {
        yield actualApi.deleteCategory(id);
        return {
            content: [{
                    type: "text",
                    text: `Category ${id} deleted successfully`
                }]
        };
    }
    catch (error) {
        console.error('Error deleting category:', error);
        return {
            content: [{
                    type: "text",
                    text: `Error deleting category: ${error.message || String(error)}`
                }],
            isError: true
        };
    }
}));
// Set budget amount
server.tool("setBudgetAmount", {
    month: z.string().describe("Budget month (YYYY-MM)"),
    categoryId: z.string().describe("Category ID"),
    amount: z.number().describe("Budget amount in cents")
}, (_a) => __awaiter(void 0, [_a], void 0, function* ({ month, categoryId, amount }) {
    try {
        yield actualApi.setBudgetAmount(month, categoryId, amount);
        return {
            content: [{
                    type: "text",
                    text: `Budget amount for category ${categoryId} in ${month} set to ${amount} cents`
                }]
        };
    }
    catch (error) {
        console.error('Error setting budget amount:', error);
        return {
            content: [{
                    type: "text",
                    text: `Error setting budget amount: ${error.message || String(error)}`
                }],
            isError: true
        };
    }
}));
// Set budget carryover
server.tool("setBudgetCarryover", {
    month: z.string().describe("Budget month (YYYY-MM)"),
    categoryId: z.string().describe("Category ID"),
    flag: z.boolean().describe("Whether to enable carryover")
}, (_a) => __awaiter(void 0, [_a], void 0, function* ({ month, categoryId, flag }) {
    try {
        yield actualApi.setBudgetCarryover(month, categoryId, flag);
        return {
            content: [{
                    type: "text",
                    text: `Budget carryover for category ${categoryId} in ${month} ${flag ? 'enabled' : 'disabled'}`
                }]
        };
    }
    catch (error) {
        console.error('Error setting budget carryover:', error);
        return {
            content: [{
                    type: "text",
                    text: `Error setting budget carryover: ${error.message || String(error)}`
                }],
            isError: true
        };
    }
}));
// ==================== PROMPTS ====================
// Budget analysis prompt
server.prompt("budget-analysis", { month: z.string().describe("Budget month (YYYY-MM)") }, ({ month }) => ({
    messages: [{
            role: "user",
            content: {
                type: "text",
                text: `Please analyze my budget for ${month}. Look at my spending categories, identify areas where I'm over or under budget, and provide recommendations for improvement.`
            }
        }]
}));
// Transaction summary prompt
server.prompt("transaction-summary", {
    accountId: z.string().describe("Account ID"),
    startDate: z.string().describe("Start date (YYYY-MM-DD)"),
    endDate: z.string().describe("End date (YYYY-MM-DD)")
}, ({ accountId, startDate, endDate }) => ({
    messages: [{
            role: "user",
            content: {
                type: "text",
                text: `Please summarize my transactions for account ${accountId} from ${startDate} to ${endDate}. Group them by category, identify my largest expenses, and highlight any unusual spending patterns.`
            }
        }]
}));
// Financial insights prompt
server.prompt("financial-insights", {}, () => ({
    messages: [{
            role: "user",
            content: {
                type: "text",
                text: `Based on my financial data, please provide insights about my spending habits, saving patterns, and budget allocation. Suggest ways I could improve my financial health.`
            }
        }]
}));
// Initialize the Actual API and start the MCP server
function startServer() {
    return __awaiter(this, void 0, void 0, function* () {
        try {
            yield initActualApi();
            // Start receiving messages on stdin and sending messages on stdout
            const transport = new StdioServerTransport();
            yield server.connect(transport);
            console.log('MCP server started');
        }
        catch (error) {
            console.error('Failed to start MCP server:', error);
            process.exit(1);
        }
    });
}
startServer();
