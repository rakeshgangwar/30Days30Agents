import os
import uuid
import asyncio
import re
from datetime import datetime
from typing import List, Optional, Union
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from pydantic_ai import Agent, DocumentUrl, BinaryContent, AudioUrl, ImageUrl
from pydantic_ai.mcp import MCPServerStdio
import tempfile
import shutil
import logging

from dotenv import load_dotenv
load_dotenv()

# Initialize FastAPI app
app = FastAPI(title="Document Analyser API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Define documents directory
DOCUMENTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "documents")
os.makedirs(DOCUMENTS_DIR, exist_ok=True)

# In-memory storage for documents and message histories
documents = {}
message_histories = {}

# Models
class DocumentBase(BaseModel):
    name: str
    type: str  # 'file', 'url', 'youtube', 'audio', or 'image'
    url: Optional[str] = None
    content_type: Optional[str] = None
    uploadedAt: datetime = Field(default_factory=datetime.now)

class DocumentResponse(DocumentBase):
    id: str

class MessageBase(BaseModel):
    role: str  # 'user' or 'assistant'
    content: str
    timestamp: datetime = Field(default_factory=datetime.now)

class MessageResponse(MessageBase):
    id: str

class UrlRequest(BaseModel):
    url: str
    name: str
    type: str = "url"  # Default to 'url', can be 'youtube', 'audio', or 'image'
    useOcr: bool = False  # For image analysis
    useLlmDescription: bool = False  # For image analysis

class AnalysisRequest(BaseModel):
    question: str

# Routes
@app.get("/documents", response_model=List[DocumentResponse])
async def get_documents():
    return [
        DocumentResponse(id=doc_id, **doc)
        for doc_id, doc in documents.items()
    ]

@app.get("/documents/{document_id}", response_model=DocumentResponse)
async def get_document(document_id: str):
    if document_id not in documents:
        raise HTTPException(status_code=404, detail="Document not found")
    return DocumentResponse(id=document_id, **documents[document_id])

@app.post("/documents/upload", response_model=DocumentResponse)
async def upload_document(file: UploadFile = File(...)):
    # Generate unique ID for the document
    doc_id = str(uuid.uuid4())
    
    # Get file content and content type
    file_content = await file.read()
    content_type = file.content_type or "application/octet-stream"
    
    # Get the original filename and extension
    original_filename = file.filename or f"document_{doc_id}"
    file_extension = os.path.splitext(original_filename)[1]
    
    # If no extension, try to determine from content type
    if not file_extension:
        if "pdf" in content_type:
            file_extension = ".pdf"
        elif "word" in content_type:
            file_extension = ".docx"
        elif "presentation" in content_type:
            file_extension = ".pptx"
        elif "excel" in content_type or "spreadsheet" in content_type:
            file_extension = ".xlsx"
        elif "text" in content_type:
            file_extension = ".txt"
        else:
            file_extension = ".bin"
    
    # Save file to documents directory with proper extension
    file_path = os.path.join(DOCUMENTS_DIR, f"{doc_id}{file_extension}")
    with open(file_path, "wb") as f:
        f.write(file_content)
    
    # Store document info
    documents[doc_id] = {
        "name": original_filename,
        "type": "file",
        "content_type": content_type,
        "uploadedAt": datetime.now()
    }
    
    # Initialize empty message history for this document
    message_histories[doc_id] = []
    
    return DocumentResponse(id=doc_id, **documents[doc_id])

@app.post("/documents/url", response_model=DocumentResponse)
async def add_document_url(request: UrlRequest):
    doc_id = str(uuid.uuid4())
    
    # Validate URL
    if not request.url.startswith("http"):
        raise HTTPException(status_code=400, detail="Invalid URL format")
    
    # Store document info
    documents[doc_id] = {
        "name": request.name,
        "type": request.type,
        "url": request.url,
        "uploadedAt": datetime.now()
    }
    
    # If it's an image, store OCR and LLM description preferences
    if request.type == "image":
        documents[doc_id]["useOcr"] = request.useOcr
        documents[doc_id]["useLlmDescription"] = request.useLlmDescription
    
    # Initialize empty message history for this document
    message_histories[doc_id] = []
    
    return DocumentResponse(id=doc_id, **documents[doc_id])

@app.post("/documents/{document_id}/analyze", response_model=dict)
async def analyze_document(document_id: str, request: AnalysisRequest):
    if document_id not in documents:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Create user message
    user_message_id = str(uuid.uuid4())
    user_message = {
        "id": user_message_id,
        "role": "user",
        "content": request.question,
        "timestamp": datetime.now()
    }
    
    # Initialize message history for this document if it doesn't exist
    if document_id not in message_histories:
        message_histories[document_id] = []
    
    # Check if this exact user message already exists in the conversation
    user_message_exists = False
    for msg in message_histories[document_id]:
        if msg["role"] == "user" and msg["content"] == request.question:
            user_message_exists = True
            break
    
    # Only add the user message if it doesn't already exist
    if not user_message_exists:
        # Add user message to conversation
        message_histories[document_id].append(user_message)
        logger.info(f"Added user message to conversation: {user_message}")
    
    # Process the document analysis synchronously
    doc = documents[document_id]
    assistant_message_id = str(uuid.uuid4())
    temp_file_path = None
    
    try:
        # Initialize agent with MCP server properly
        server = MCPServerStdio('markitdown-mcp', args=[])
        agent = Agent('openai:gpt-4o', mcp_servers=[server])
        
        # Run the agent with MCP servers context manager
        async with agent.run_mcp_servers():
            # Prepare the message content based on document type
            if doc["type"] == "file":
                # For file documents - use the file directly from documents directory
                original_filename = doc.get("name", f"document_{document_id}")
                logger.info(f"Original filename: {original_filename}")
                
                file_extension = os.path.splitext(original_filename)[1]
                logger.info(f"Detected file extension: {file_extension}")
                
                if not file_extension:
                    # Try to determine extension from content type
                    content_type = doc.get("content_type", "")
                    logger.info(f"Content type: {content_type}")
                    
                    if "pdf" in content_type:
                        file_extension = ".pdf"
                    elif "word" in content_type:
                        file_extension = ".docx"
                    elif "presentation" in content_type:
                        file_extension = ".pptx"
                    elif "excel" in content_type or "spreadsheet" in content_type:
                        file_extension = ".xlsx"
                    elif "text" in content_type:
                        file_extension = ".txt"
                    else:
                        file_extension = ".bin"
                    
                    logger.info(f"Determined file extension from content type: {file_extension}")
                
                # Use the file directly from the documents directory
                file_path = os.path.join(DOCUMENTS_DIR, f"{document_id}{file_extension}")
                file_path = os.path.abspath(file_path)
                logger.info(f"File path: {file_path}")
                
                # Create message with question and reference to the file
                message_content = f"Analyze this document at {file_path} and answer the following question: {request.question}"
                logger.info(f"Message content: {message_content}")
                
                # For follow-up questions, don't use message history as it seems to cause issues
                # Instead, run the agent with just the new message that includes document reference
                result = await agent.run(message_content)
                logger.info(f"Result from agent: {result}")
                logger.info(f"Result output: {result.output}")
            elif doc["type"] == "youtube":
                # For YouTube documents
                url = doc["url"]
                logger.info(f"YouTube URL: {url}")
                
                # Create message content with YouTube URL - always include URL
                message_content = f"Analyze this YouTube video at {url} and answer the following question: {request.question}"
                logger.info(f"Message content: {message_content}")
                
                # For follow-up questions, don't use message history
                result = await agent.run(message_content)
                logger.info(f"Result from agent: {result}")
                logger.info(f"Result output: {result.output}")
            elif doc["type"] == "audio":
                # For audio documents
                url = doc["url"]
                logger.info(f"Audio URL: {url}")
                
                # Create message content with audio URL - always include URL
                message_content = f"Analyze this audio file at {url} and answer the following question: {request.question}"
                logger.info(f"Message content: {message_content}")
                
                # For follow-up questions, don't use message history
                result = await agent.run(message_content)
                logger.info(f"Result from agent: {result}")
                logger.info(f"Result output: {result.output}")
            elif doc["type"] == "image":
                # For image documents
                url = doc["url"]
                use_ocr = doc.get("useOcr", False)
                use_llm_description = doc.get("useLlmDescription", False)
                logger.info(f"Image URL: {url}, OCR: {use_ocr}, LLM Description: {use_llm_description}")
                
                # Create message content with image URL - always include URL
                prompt = f"Analyze this image at {url}"
                if use_ocr:
                    prompt += " using OCR to extract any text"
                if use_llm_description:
                    prompt += " and generate a detailed description of the image content"
                prompt += f" and answer the following question: {request.question}"
                message_content = prompt
                logger.info(f"Message content: {message_content}")
                
                # For follow-up questions, don't use message history
                result = await agent.run(message_content)
                logger.info(f"Result from agent: {result}")
                logger.info(f"Result output: {result.output}")
            else:
                # For URL documents
                url = doc["url"]
                logger.info(f"Document URL: {url}")
                
                # Create message content with document URL - always include URL
                message_content = f"Analyze this document at {url} and answer the following question: {request.question}"
                logger.info(f"Message content: {message_content}")
                
                # For follow-up questions, don't use message history
                result = await agent.run(message_content)
                logger.info(f"Result from agent: {result}")
                logger.info(f"Result output: {result.output}")
        
        # Create the assistant message
        assistant_message = {
            "id": assistant_message_id,
            "role": "assistant",
            "content": result.output,
            "timestamp": datetime.now()
        }
        logger.info(f"Adding assistant message to conversation: {assistant_message}")
        
        # Add the assistant message to the conversation history
        message_histories[document_id].append(assistant_message)
        
        # Return both messages
        return {
            "user_message": user_message,
            "assistant_message": assistant_message
        }
    except Exception as e:
        # Handle errors
        error_message = f"Error analyzing document: {str(e)}"
        logger.error(f"Error: {error_message}")
        error_assistant_message = {
            "id": assistant_message_id,
            "role": "assistant",
            "content": error_message,
            "timestamp": datetime.now()
        }
        message_histories[document_id].append(error_assistant_message)
        return {
            "user_message": user_message,
            "assistant_message": error_assistant_message
        }

@app.get("/documents/{document_id}/conversation")
async def get_conversation(document_id: str):
    if document_id not in documents:
        raise HTTPException(status_code=404, detail="Document not found")
    
    if document_id not in message_histories:
        message_histories[document_id] = []
    
    # Log the conversation being returned
    logger.info(f"Returning conversation for document {document_id}: {message_histories[document_id]}")
    logger.info(f"Conversation length: {len(message_histories[document_id])}")
    
    # Log the roles of messages in the conversation
    roles = [msg["role"] for msg in message_histories[document_id]]
    logger.info(f"Message roles in conversation: {roles}")
    
    # Return a deep copy of the conversation to avoid any reference issues
    import copy
    return copy.deepcopy(message_histories[document_id])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
