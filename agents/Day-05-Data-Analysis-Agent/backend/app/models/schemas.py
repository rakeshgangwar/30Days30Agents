"""
Data Analysis Agent - Schema Models

This module contains Pydantic models for request and response validation.
"""

from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any, Union


class QueryRequest(BaseModel):
    """Model for natural language query requests."""
    query: str = Field(..., description="Natural language query to analyze data")


class CSVUploadResponse(BaseModel):
    """Model for CSV upload response."""
    success: bool = Field(..., description="Whether the upload was successful")
    message: str = Field(..., description="Status message")
    columns: Optional[List[str]] = Field(None, description="List of column names in the CSV")
    rows: Optional[int] = Field(None, description="Number of rows in the CSV")
    preview: Optional[List[Dict[str, Any]]] = Field(None, description="Preview of the first few rows")
    error: Optional[str] = Field(None, description="Error message if upload failed")


class DBConnectionRequest(BaseModel):
    """Model for database connection requests."""
    db_type: str = Field(..., description="Type of database (sqlite, postgresql)")
    connection_params: Dict[str, Any] = Field(..., description="Connection parameters")


class DBConnectionResponse(BaseModel):
    """Model for database connection response."""
    success: bool = Field(..., description="Whether the connection was successful")
    message: str = Field(..., description="Status message")
    tables: Optional[List[str]] = Field(None, description="List of tables in the database")
    error: Optional[str] = Field(None, description="Error message if connection failed")


class VisualizationData(BaseModel):
    """Model for visualization data."""
    type: str = Field(..., description="Type of visualization (plotly)")
    figure: Dict[str, Any] = Field(..., description="Plotly figure JSON")


class AnalysisResult(BaseModel):
    """Model for analysis results."""
    text: str = Field(..., description="Textual analysis result")
    data: Optional[List[Dict[str, Any]]] = Field(None, description="Tabular data result")
    visualization: Optional[VisualizationData] = Field(None, description="Visualization data")
    code: Optional[str] = Field(None, description="Generated code (Python/SQL)")


class QueryResponse(BaseModel):
    """Model for query response."""
    success: bool = Field(..., description="Whether the query was successful")
    result: Optional[AnalysisResult] = Field(None, description="Analysis result")
    error: Optional[str] = Field(None, description="Error message if query failed")


class HealthCheckResponse(BaseModel):
    """Model for health check response."""
    status: str = Field(..., description="API status")
    version: str = Field(..., description="API version")
