# Document Analyser

A powerful web application that allows users to upload documents or add links for AI-powered analysis. The application leverages PydanticAI with an MCP server to provide in-depth document analysis and question-answering capabilities.

## Core Functionality

### Document Analysis
- **File Analysis**: Upload and analyze various document formats (PDF, DOC, DOCX, TXT, XLSX, XLS, PPTX, etc.)
- **URL Analysis**: Add and analyze content from web URLs
- **Media Analysis**:
  - **YouTube Videos**: Extract and analyze transcripts from YouTube videos
  - **Audio Files**: Transcribe and analyze audio content
  - **Images**: Analyze images with optional OCR for text extraction and AI-generated descriptions

### Interactive Question-Answering
- Maintain persistent conversation history for each document
- Ask follow-up questions about document content
- Receive AI-generated responses with markdown formatting support

## Supported File Types
- Documents: PDF, DOC, DOCX, TXT
- Spreadsheets: XLSX, XLS, CSV
- Presentations: PPTX
- Media: JPG, PNG, MP3, WAV
- Other: EPUB, ZIP, JSON, XML

## Technical Implementation

### Backend (FastAPI)
The application uses a robust FastAPI backend that:
- Manages document uploads and storage
- Processes different document types (files, URLs, YouTube videos, audio, images)
- Integrates with PydanticAI and MarkItDown MCP for document analysis
- Maintains conversation histories for each document
- Provides a RESTful API for the frontend

### API Endpoints
- `GET /documents` - Retrieve all documents
- `GET /documents/{document_id}` - Get a specific document's metadata
- `POST /documents/upload` - Upload a document file
- `POST /documents/url` - Add a document URL, YouTube video, audio URL, or image URL
- `POST /documents/{document_id}/analyze` - Analyze a document with a specific question
- `GET /documents/{document_id}/conversation` - Retrieve conversation history for a document

## Project Structure

```
DocumentAnalyser/
├── frontend/            # Frontend React application
│   └── frontend-app/    # React TypeScript application
├── documents/           # Uploaded document storage
├── .env                 # Environment variables
├── api.py               # FastAPI backend
├── main.py              # Original PydanticAI agent script
└── README.md            # This file
```

## Setup Instructions

### Backend Setup

1. Make sure you have Python 3.8+ installed
2. Install the required Python packages:

```bash
pip install -r requirements.txt
```

3. Set up your environment variables in `.env` file (API keys, etc.)
4. Run the FastAPI backend:

```bash
uvicorn api:app --reload
```

The API will be available at http://localhost:8000

### Frontend Setup

1. Make sure you have Node.js and pnpm installed
2. Navigate to the frontend directory:

```bash
cd frontend/frontend-app
```

3. Install dependencies:

```bash
pnpm install
```

4. Start the development server:

```bash
pnpm run dev
```

The frontend will be available at http://localhost:5173

## Technologies Used

- **Backend**: FastAPI, PydanticAI, Python
- **AI**: PydanticAI with MarkItDown MCP server
- **Frontend**: React, TypeScript, Vite, Shadcn UI components
- **Document Processing**: AI-powered analysis for documents, YouTube transcripts, audio and images
