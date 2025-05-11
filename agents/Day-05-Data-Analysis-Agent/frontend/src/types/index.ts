// API Response Types
export interface ApiResponse<T> {
  success: boolean;
  result?: T;
  error?: string;
}

// CSV Types
export interface CSVUploadResponse {
  success: boolean;
  message: string;
  columns?: string[];
  rows?: number;
  preview?: Record<string, any>[];
  error?: string;
}

// Database Types
export interface DBConnectionRequest {
  db_type: string;
  connection_params: Record<string, any>;
}

export interface DBConnectionResponse {
  success: boolean;
  message: string;
  tables?: string[];
  connection_id?: string;
  error?: string;
}

// Query Types
export interface QueryRequest {
  query: string;
}

// Visualization Types
export interface VisualizationData {
  type: string;
  figure: Record<string, any>;
}

// Analysis Result Types
export interface AnalysisResult {
  text: string;
  data?: Record<string, any>[];
  visualization?: VisualizationData;
  code?: string;
}

export interface QueryResponse {
  success: boolean;
  result?: AnalysisResult;
  error?: string;
}

// Application State Types
export type DataSourceType = 'csv' | 'database' | null;

export interface CSVState {
  fileId: string | null;
  fileName: string | null;
  columns: string[];
  rows: number | null;
  preview: Record<string, any>[];
}

export interface DatabaseState {
  connectionId: string | null;
  dbType: string | null;
  tables: string[];
  connected: boolean;
}

export interface QueryState {
  query: string;
  loading: boolean;
  result: AnalysisResult | null;
  error: string | null;
}

export interface AppState {
  dataSource: DataSourceType;
  csv: CSVState;
  database: DatabaseState;
  query: QueryState;
}
