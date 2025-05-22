# Email Assistant Agent

An AI-powered email management assistant built with the Agno framework that helps users efficiently manage their inbox by summarizing emails, drafting replies, prioritizing messages, and automating email-related tasks.

## Features

- **Email Summarization**: Quickly understand the key points of individual emails or entire threads
- **Smart Reply Drafting**: Generate contextually appropriate email replies based on your instructions
- **Email Prioritization**: Automatically categorize and prioritize emails by importance and urgency
- **Action Item Extraction**: Identify and list tasks, requests, and required actions from emails
- **Natural Language Search**: Find emails using conversational queries instead of rigid search syntax
- **Email Templates**: Generate and customize templates for common email scenarios

## Tech Stack

- **Framework**: [Agno](https://docs.agno.com/) - A lightweight, high-performance library for building Agents
- **Models**: OpenAI GPT-4o or Anthropic Claude
- **Email APIs**: Gmail API and Microsoft Graph API (for Outlook/Office 365)
- **UI**: Streamlit web application

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/email-assist.git
   cd email-assist
   ```

2. Set up a virtual environment and install dependencies:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   uv pip install -e .
   ```

3. Set up API credentials:
   - For Gmail: Create a project in [Google Cloud Console](https://console.cloud.google.com/), enable the Gmail API, and download the credentials.json file
   - For Microsoft Graph: Register an application in the [Azure Portal](https://portal.azure.com/) and note your client ID, client secret, and tenant ID

4. Create a `.env` file with your API keys:
   ```
   # Choose one model provider
   OPENAI_API_KEY=your_openai_api_key
   ANTHROPIC_API_KEY=your_anthropic_api_key
   ```

## Usage

### Running the Streamlit UI

```bash
python main.py --ui
```

This will start the Streamlit web application at http://localhost:8501.

### Authentication

1. Select your email provider (Gmail or Microsoft Outlook) in the sidebar
2. Follow the authentication instructions:
   - For Gmail: Upload your credentials.json file and complete the OAuth flow
   - For Microsoft Outlook: Enter your client ID, client secret, and tenant ID, then complete the OAuth flow

### Using the Assistant

Once authenticated, you can use the different tabs in the UI to:
- View and prioritize your inbox
- Summarize emails and threads
- Draft replies to emails
- Search for emails using natural language
- Generate email templates
- Ask the assistant general questions about your emails

## Project Structure

```
email-assist/
├── email_assist/           # Main package
│   ├── auth/               # Authentication modules
│   │   ├── gmail_auth.py   # Gmail OAuth authentication
│   │   └── ms_graph_auth.py # Microsoft Graph authentication
│   ├── tools/              # Email API tools
│   │   ├── email_tools.py  # Agno tools wrapper
│   │   ├── gmail_tools.py  # Gmail API tools
│   │   └── ms_graph_tools.py # Microsoft Graph API tools
│   ├── ui/                 # User interface
│   │   └── streamlit_app.py # Streamlit web application
│   ├── email_agent.py      # Main agent implementation
│   └── __init__.py
├── main.py                 # Entry point
├── pyproject.toml          # Project metadata and dependencies
└── README.md               # Project documentation
```

## Limitations

- Requires secure handling of email credentials and content (privacy concern)
- Summarization or drafting might miss context or make errors
- Actions taken (like sending emails) are irreversible and require user confirmation
- Dependent on the reliability and features of the email provider's API

## Future Enhancements

- Support for additional email providers
- Advanced email filtering and categorization
- Integration with calendar APIs for scheduling
- Integration with task management tools
- Email analytics and insights
- Mobile application support

## License

MIT
