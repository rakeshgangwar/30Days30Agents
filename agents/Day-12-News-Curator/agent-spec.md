# Day 12: News Curator Agent

## Agent Purpose
Aggregates news articles from various sources based on user-defined topics and preferences, providing summaries and personalized news briefings.

## Key Features
- News fetching from multiple sources (APIs, RSS feeds)
- Filtering news based on keywords, topics, sources, and recency
- Summarization of articles or groups of articles
- Personalization based on user interests
- Delivery of news briefings (e.g., daily email, UI display)
- Sentiment analysis of news articles (optional)

## Example Queries/Configurations
- "Show me the latest news about artificial intelligence from TechCrunch and Wired."
- "Summarize the top 5 headlines related to climate change today."
- "Create a daily briefing on stock market news, focusing on the tech sector."
- "Find positive news articles about renewable energy."
- "Configure my interests: AI, space exploration, local politics."

## Tech Stack
- **Framework**: LangChain or CrewAI (for potential multi-agent summarization/analysis)
- **Model**: GPT-3.5-Turbo or GPT-4
- **Tools**: News APIs (e.g., NewsAPI.org, GNews), RSS feed parsers (feedparser), Web scraping tools (BeautifulSoup/Scrapy, for sources without APIs), Summarization logic
- **Storage**: Database (for user preferences, curated articles, summaries)
- **UI**: Streamlit, Web application, or email delivery

## Possible Integrations
- Social media platforms for sharing curated news
- Note-taking apps (Evernote, Notion) for saving articles
- Fact-checking APIs
- Language translation APIs
- https://www.freshrss.org/
- https://github.com/rakeshgangwar/freshrss-server

## Architecture Considerations

### Input Processing
- Parsing user preferences for topics, keywords, sources, and delivery frequency
- Handling requests for specific news searches or summaries
- Processing fetched data from APIs and RSS feeds (JSON, XML)

### Knowledge Representation
- User profile storing interests, preferred sources, and delivery settings
- Database schema for storing fetched articles (URL, title, source, timestamp, content/summary)
- Representation of curated news briefings

### Decision Logic
- Filtering logic based on keywords, topics, sources, recency, and user preferences
- Relevance scoring for articles
- Summarization strategy (individual article summaries, topic cluster summaries)
- Selection of articles for personalized briefings
- Optional: Sentiment analysis classification

### Tool Integration
- News API clients and RSS feed parsers
- Web scraping tools for fetching full article text if needed (respecting robots.txt)
- LLM for summarization and potentially topic classification/sentiment analysis
- Database ORM for storing data
- Email delivery service (if applicable)

### Output Formatting
- Structured news briefings with headlines, summaries, sources, and links
- Categorized news items
- Optional sentiment indicators
- Clear presentation in UI or formatted email

### Memory Management
- Storing user preferences and historical interests
- Keeping track of recently delivered articles to avoid duplicates
- Caching fetched articles or summaries

### Error Handling
- Handling errors from News APIs or RSS feed fetching (e.g., invalid URL, rate limits)
- Managing failures in web scraping or content extraction
- Dealing with summarization errors or low-quality summaries
- Graceful handling if no relevant news is found for specific topics

## Implementation Flow
1. Agent fetches news articles from configured sources (APIs, RSS) based on user preferences or a specific query.
2. Agent filters articles based on keywords, topics, recency, and relevance.
3. Agent extracts key information or full text from articles.
4. Agent generates summaries for selected articles or topic clusters using an LLM.
5. (Optional) Agent performs sentiment analysis.
6. Agent compiles a personalized news briefing based on user preferences.
7. Agent delivers the briefing via the chosen method (UI display, email).

## Scaling Considerations
- Handling a large number of news sources and high frequency of updates
- Efficiently processing and summarizing large volumes of text
- Supporting many users with diverse preferences
- Implementing near real-time news monitoring

## Limitations
- Dependent on the availability and quality of news sources/APIs.
- Summarization may miss nuances or introduce bias.
- Filtering might exclude relevant articles or include irrelevant ones.
- Cannot guarantee the veracity of news articles; relies on source credibility.
- Web scraping can be unreliable and may face legal/ethical constraints.