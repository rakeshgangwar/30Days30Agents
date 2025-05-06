# Day 26: Investment Advisor Agent (Informational Only)

**IMPORTANT DISCLAIMER:** This agent is for informational and educational purposes ONLY. It does NOT provide financial advice. Any information related to stocks, markets, or investment strategies is purely illustrative and should NOT be taken as a recommendation to buy, sell, or hold any securities. Always consult with a qualified financial advisor before making any investment decisions.

## Agent Purpose
Provides information about financial markets, investment concepts, and analyzes stock data based on user queries. **Does not give personalized investment advice or recommendations.**

## Key Features
- Fetching current stock prices and market data
- Providing historical stock performance data and charts (using libraries)
- Explaining investment terms and concepts (e.g., diversification, ETFs, P/E ratio)
- Summarizing financial news related to specific stocks or markets
- Analyzing stock fundamentals based on publicly available data (e.g., P/E, EPS, market cap) - **for informational purposes only**
- Comparing stocks based on specific metrics - **for informational purposes only**

## Example Queries/Tasks
- "What is the current price of Apple (AAPL) stock?"
- "Show me the price history for Tesla (TSLA) over the past year."
- "Explain what a mutual fund is."
- "Find recent news articles about Microsoft (MSFT)."
- "What is the P/E ratio for Google (GOOGL)?"
- "Compare the market cap of Amazon (AMZN) and Walmart (WMT)."
- **Crucially NOT:** "Should I buy AAPL stock?" or "What stocks should I invest in?"

## Tech Stack
- **Framework**: LangChain
- **Model**: GPT-4 or Claude-2/3
- **Tools**: Financial data APIs (e.g., Alpha Vantage, Yahoo Finance via `yfinance`, Polygon.io, IEX Cloud), News APIs (e.g., NewsAPI), Web search, Data visualization libraries (Matplotlib, Plotly)
- **Storage**: Optional: Database for user watchlist or saved queries
- **UI**: Streamlit, Web application, Command-line interface

## Possible Integrations
- Brokerage APIs (for fetching portfolio data - view only, **NO TRADING**)
- Portfolio tracking tools

## Architecture Considerations

### Input Processing
- Parsing user queries for stock tickers, company names, financial terms, date ranges, comparison requests
- Validating stock tickers
- **Strict filtering to reject requests for financial advice or recommendations.**

### Knowledge Representation
- LLM's knowledge of financial concepts and terminology
- Structured data retrieved from financial APIs (prices, fundamentals, news)
- User's watchlist (optional)

### Decision Logic
- Identifying the type of information requested (price, history, news, explanation, analysis, comparison)
- Formulating queries for financial data APIs and news APIs
- Selecting appropriate data points for analysis or comparison based on user request
- **Reinforcing the "information only, not advice" disclaimer in responses.**
- Logic for generating charts from historical data

### Tool Integration
- Financial data API clients (`yfinance`, Alpha Vantage wrapper, etc.)
- News API clients
- Web search tool (for explanations or supplementary info)
- Data visualization libraries for plotting charts
- LLM for explanations, summarization, and NLU

### Output Formatting
- Clear presentation of stock prices, historical data, and fundamental metrics
- Concise explanations of financial terms
- Summarized news articles with sources
- Generated charts (displayed in UI or saved as files)
- **Prominent display of disclaimers with every response containing market data or analysis.**

### Memory Management
- Caching API responses (especially for less volatile data like fundamentals)
- Storing user watchlist (optional)
- Secure handling of financial API keys

### Error Handling
- Handling errors from financial/news APIs (invalid ticker, rate limits, data unavailable)
- Managing invalid user inputs (unrecognized tickers, ambiguous terms)
- Gracefully declining requests for financial advice
- Handling data visualization errors

## Implementation Flow
1. User submits a query related to stocks, markets, or financial concepts.
2. **Agent checks if the query requests financial advice. If yes, decline with a disclaimer.**
3. Agent parses the valid query to identify intent, entities (tickers, terms), and parameters.
4. Agent selects appropriate tools (financial API, news API, web search, LLM).
5. Agent fetches data using the tools (stock prices, history, news, fundamentals).
6. Agent processes the data (e.g., calculates metrics, prepares data for charting).
7. Agent uses LLM to generate explanations or summaries if requested.
8. Agent formats the results (text, tables, charts).
9. **Agent prepends/appends the mandatory "Not financial advice" disclaimer.**
10. Agent presents the information to the user.

## Scaling Considerations
- Managing API costs and rate limits for financial data providers
- Handling a large number of stock tickers and data points
- Providing near real-time data updates
- Ensuring data accuracy from various sources

## Limitations
- **Strictly informational; cannot provide personalized advice.**
- Data accuracy and timeliness depend on the underlying APIs.
- Financial markets are complex; simplified analysis may be misleading.
- Does not consider user's personal financial situation, risk tolerance, or goals.
- Free financial APIs often have significant limitations (rate limits, data coverage, delay).
- LLM knowledge about finance might be outdated or incorrect. Requires grounding in real-time data.