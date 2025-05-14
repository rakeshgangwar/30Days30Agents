# Day 7: Task Automation Agent - User Journey & Prompt Handling

This document outlines typical user journeys and how the Task Automation Agent, built with PydanticAI and Beehive, will handle sample prompts. This aligns with the example queries in [`agent-spec.md`](../agent-spec.md:13).

## User Journey Overview

1.  **User Input**: The user provides a task description in natural language via a UI (Streamlit/CLI) or API.
2.  **PydanticAI - Parsing & Understanding**:
    *   The PydanticAI layer receives the input.
    *   An LLM (e.g., GPT-4) processes the text, guided by Pydantic models, to extract intent, entities, parameters, and desired actions.
    *   The output is a structured representation of the task (e.g., a `UserTaskInput` Pydantic model).
3.  **PydanticAI - Planning & Decomposition**:
    *   The PydanticAI agent, using its LLM capabilities and defined logic (potentially `Pydantic Graph`), decomposes the structured task into a sequence of executable steps (`PlannedStep` models).
    *   Each step might involve calling a PydanticAI tool or delegating to Beehive.
4.  **Tool/Engine Selection**:
    *   **PydanticAI Tools**: For tasks requiring direct execution by the agent (e.g., complex logic, immediate web scraping not suitable for Beehive, custom file operations).
    *   **Beehive (via MCP Server)**: For event-driven tasks, recurring schedules, or interactions with services where Beehive Hives are already available and efficient (e.g., RSS monitoring, email sending/receiving based on simple triggers).
5.  **Execution**:
    *   **PydanticAI Tools**: Executed directly within the PydanticAI agent's environment. Results are validated against Pydantic output models.
    *   **Beehive Tasks**: The `BeehiveControlTool` (a PydanticAI tool) sends a structured request to the `beehive-mcp-server`, which then instructs the Beehive instance to configure or trigger a Bee/workflow.
6.  **Monitoring & Feedback**:
    *   The PydanticAI layer monitors the overall workflow.
    *   For Beehive tasks, status updates can be retrieved via the MCP server.
    *   The user receives confirmations, progress updates, and final results or error messages.
7.  **Completion/Output**:
    *   The agent provides the final output, which could be a message, a generated file, or a status update.

## Sample Prompts & Handling Strategy

These examples are drawn from [`agent-spec.md`](../agent-spec.md:13).

### 1. "Check my unread emails, summarize important ones, and draft replies."

*   **User Input**: "Check my unread emails from today related to 'Project Alpha', summarize them, and draft a polite 'will look into this' reply for each."
*   **PydanticAI - Parsing & Understanding**:
    *   Intent: Email processing (read, summarize, draft reply).
    *   Entities: Email source (user's account), filter criteria (unread, today, "Project Alpha"), summary requirement, reply content template.
    *   Structured Output: `UserTaskInput(action="process_emails", source="default_email", filters={"status": "unread", "date": "today", "keywords": ["Project Alpha"]}, summarize=True, draft_reply_template="Will look into this.")`
*   **PydanticAI - Planning & Decomposition**:
    1.  `PlannedStep(tool="EmailTool", action="fetch_emails", params={"status": "unread", "date": "today", "keywords": ["Project Alpha"]})`
    2.  For each fetched email: `PlannedStep(tool="LLMTool", action="summarize", params={"text": email_content, "max_length": 100})`
    3.  For each summarized email: `PlannedStep(tool="LLMTool", action="draft_reply", params={"context": summary, "sender": email_sender, "template": "Will look into this."})`
    4.  `PlannedStep(tool="UserInteractionTool", action="present_drafts", params={"drafts": all_drafted_replies})`
*   **Tool/Engine Selection**:
    *   `EmailTool`: A PydanticAI tool that interacts with an email API (e.g., Gmail API, Microsoft Graph). This could potentially use a Beehive Email Hive via MCP if the interaction is simple enough (e.g., just fetching unread count), but direct API access via a PydanticAI tool offers more control for complex filtering and actions.
    *   `LLMTool`: A PydanticAI tool for direct LLM calls for summarization and drafting.
    *   `UserInteractionTool`: A PydanticAI tool to present results to the user (e.g., via Streamlit UI).
*   **Execution**:
    *   PydanticAI agent orchestrates the steps, calling its internal tools.
*   **Output**: List of summaries and drafted replies presented to the user.

### 2. "Monitor this website for price drops on product X and notify me."

*   **User Input**: "Monitor `https://example.com/productX` for a price drop below $50 and send me an email if it happens."
*   **PydanticAI - Parsing & Understanding**:
    *   Intent: Web monitoring, notification.
    *   Entities: URL (`https://example.com/productX`), target element (price), condition (< $50), notification channel (email).
    *   Structured Output: `UserTaskInput(action="monitor_website_price", url="https://example.com/productX", price_target={"value": 50, "condition": "less_than"}, notification_method="email")`
*   **PydanticAI - Planning & Decomposition**:
    1.  `PlannedStep(tool="BeehiveControlTool", action="setup_web_monitor", params={"url": "https://example.com/productX", "css_selector_price": "span.price", "target_value": 50, "condition": "less_than", "callback_action": "send_email", "callback_params": {"to": user_email, "subject": "Price Drop Alert!"}})`
*   **Tool/Engine Selection**:
    *   `BeehiveControlTool`: This is the ideal scenario for Beehive. A Beehive Web Hive can periodically check the website, and an Email Hive can send the notification.
*   **Execution**:
    *   PydanticAI agent uses `BeehiveControlTool` to configure a new monitoring task in Beehive via the MCP server.
    *   Beehive runs the monitoring task independently.
*   **Output**: User receives an email if/when the price drops. PydanticAI agent might confirm "Monitoring task set up."

### 3. "Every morning, get the weather forecast and send it to my Slack channel."

*   **User Input**: "Every morning at 8 AM, get the weather forecast for London and post it to the #general Slack channel."
*   **PydanticAI - Parsing & Understanding**:
    *   Intent: Scheduled information retrieval and messaging.
    *   Entities: Schedule (daily, 8 AM), information type (weather forecast), location (London), destination (Slack, #general).
    *   Structured Output: `UserTaskInput(action="scheduled_weather_to_slack", schedule={"type": "daily", "time": "08:00"}, location="London", slack_channel="#general")`
*   **PydanticAI - Planning & Decomposition**:
    1.  `PlannedStep(tool="BeehiveControlTool", action="setup_scheduled_task", params={"schedule": "0 8 * * *", "task_type": "weather_to_slack", "task_params": {"location": "London", "slack_channel": "#general"}})`
*   **Tool/Engine Selection**:
    *   `BeehiveControlTool`: Beehive is excellent for scheduled tasks. It could have a "Weather Hive" (or a generic HTTP Hive to call a weather API) and a "Slack Hive". The MCP server would expose a way to define a Bee that chains these.
*   **Execution**:
    *   PydanticAI agent uses `BeehiveControlTool` to set up the recurring task in Beehive.
    *   Beehive executes the task daily.
*   **Output**: Daily weather updates in the specified Slack channel. PydanticAI agent confirms "Scheduled weather report set up."

### 4. "Extract data from this PDF table and save it to a CSV file."

*   **User Input**: "Extract the table from page 5 of `report.pdf` and save it as `data.csv`."
*   **PydanticAI - Parsing & Understanding**:
    *   Intent: Data extraction (PDF to CSV).
    *   Entities: Source file (`report.pdf`), page number (5), target format (CSV), output filename (`data.csv`).
    *   Structured Output: `UserTaskInput(action="extract_pdf_table_to_csv", source_pdf="report.pdf", page_number=5, output_csv="data.csv")`
*   **PydanticAI - Planning & Decomposition**:
    1.  `PlannedStep(tool="FileTool", action="read_pdf_page", params={"file_path": "report.pdf", "page_number": 5})`
    2.  `PlannedStep(tool="LLMTool", action="extract_table_from_text", params={"text_content": pdf_page_content})` (or a specialized table extraction tool if available)
    3.  `PlannedStep(tool="DataConversionTool", action="convert_to_csv", params={"data_structure": extracted_table_data})`
    4.  `PlannedStep(tool="FileTool", action="write_file", params={"file_path": "data.csv", "content": csv_content})`
*   **Tool/Engine Selection**:
    *   `FileTool`: A PydanticAI tool for reading/writing local files.
    *   `LLMTool` / `TableExtractionTool`: A PydanticAI tool. LLMs can be surprisingly good at table extraction from text, or a dedicated library could be wrapped.
    *   `DataConversionTool`: A PydanticAI tool for converting structured data (e.g., list of lists from LLM) to CSV format.
*   **Execution**:
    *   PydanticAI agent orchestrates these steps using its internal tools.
*   **Output**: `data.csv` file created. Agent confirms "Table extracted and saved to data.csv."

### 5. "Rename all files in this folder to include today's date."

*   **User Input**: "In the `~/Documents/Reports` folder, rename all `.docx` files to `YYYY-MM-DD_filename.docx`."
*   **PydanticAI - Parsing & Understanding**:
    *   Intent: Batch file renaming.
    *   Entities: Folder path (`~/Documents/Reports`), file pattern (`.docx`), new name format (`YYYY-MM-DD_filename.docx`).
    *   Structured Output: `UserTaskInput(action="batch_rename_files", folder_path="~/Documents/Reports", file_pattern="*.docx", rename_format="<date>_<original_name>")`
*   **PydanticAI - Planning & Decomposition**:
    1.  `PlannedStep(tool="FileTool", action="list_files", params={"folder_path": "~/Documents/Reports", "pattern": "*.docx"})`
    2.  For each file found:
        `PlannedStep(tool="FileTool", action="rename_file", params={"original_path": file_path, "new_name_format": "<date>_<original_name>"})` (The tool would handle date formatting).
*   **Tool/Engine Selection**:
    *   `FileTool`: A PydanticAI tool with capabilities for listing and renaming files.
*   **Execution**:
    *   PydanticAI agent executes the file operations.
*   **Output**: Files renamed. Agent confirms "Files in `~/Documents/Reports` renamed."

This approach allows for flexibility, leveraging PydanticAI for complex understanding, planning, and direct execution, while offloading suitable event-driven and scheduled tasks to Beehive for efficiency and robustness.