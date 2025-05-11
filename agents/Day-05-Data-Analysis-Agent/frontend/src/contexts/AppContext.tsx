import React, { createContext, useContext, useReducer, ReactNode } from 'react';
import type {
  AppState,
  DataSourceType,
  CSVState,
  DatabaseState,
  QueryState,
  AnalysisResult
} from '../types/index';

// Define initial state
const initialState: AppState = {
  dataSource: null,
  csv: {
    fileId: null,
    fileName: null,
    columns: [],
    rows: null,
    preview: [],
  },
  database: {
    connectionId: null,
    dbType: null,
    tables: [],
    connected: false,
  },
  query: {
    query: '',
    loading: false,
    result: null,
    error: null,
  },
};

// Define action types
type ActionType =
  | { type: 'SET_DATA_SOURCE'; payload: DataSourceType }
  | { type: 'SET_CSV_DATA'; payload: Partial<CSVState> }
  | { type: 'RESET_CSV_DATA' }
  | { type: 'SET_DB_CONNECTION'; payload: Partial<DatabaseState> }
  | { type: 'RESET_DB_CONNECTION' }
  | { type: 'SET_QUERY'; payload: string }
  | { type: 'SET_QUERY_LOADING'; payload: boolean }
  | { type: 'SET_QUERY_RESULT'; payload: AnalysisResult }
  | { type: 'SET_QUERY_ERROR'; payload: string }
  | { type: 'RESET_QUERY' }
  | { type: 'RESET_ALL' };

// Create reducer function
const appReducer = (state: AppState, action: ActionType): AppState => {
  switch (action.type) {
    case 'SET_DATA_SOURCE':
      return {
        ...state,
        dataSource: action.payload,
      };

    case 'SET_CSV_DATA':
      return {
        ...state,
        csv: {
          ...state.csv,
          ...action.payload,
        },
      };

    case 'RESET_CSV_DATA':
      return {
        ...state,
        csv: initialState.csv,
      };

    case 'SET_DB_CONNECTION':
      return {
        ...state,
        database: {
          ...state.database,
          ...action.payload,
        },
      };

    case 'RESET_DB_CONNECTION':
      return {
        ...state,
        database: initialState.database,
      };

    case 'SET_QUERY':
      return {
        ...state,
        query: {
          ...state.query,
          query: action.payload,
        },
      };

    case 'SET_QUERY_LOADING':
      return {
        ...state,
        query: {
          ...state.query,
          loading: action.payload,
        },
      };

    case 'SET_QUERY_RESULT':
      return {
        ...state,
        query: {
          ...state.query,
          result: action.payload,
          loading: false,
          error: null,
        },
      };

    case 'SET_QUERY_ERROR':
      return {
        ...state,
        query: {
          ...state.query,
          error: action.payload,
          loading: false,
        },
      };

    case 'RESET_QUERY':
      return {
        ...state,
        query: initialState.query,
      };

    case 'RESET_ALL':
      return initialState;

    default:
      return state;
  }
};

// Create context
interface AppContextType {
  state: AppState;
  dispatch: React.Dispatch<ActionType>;
}

const AppContext = createContext<AppContextType | undefined>(undefined);

// Create provider component
interface AppProviderProps {
  children: ReactNode;
}

export const AppProvider: React.FC<AppProviderProps> = ({ children }) => {
  const [state, dispatch] = useReducer(appReducer, initialState);

  return (
    <AppContext.Provider value={{ state, dispatch }}>
      {children}
    </AppContext.Provider>
  );
};

// Create custom hook for using the context
export const useAppContext = () => {
  const context = useContext(AppContext);

  if (context === undefined) {
    throw new Error('useAppContext must be used within an AppProvider');
  }

  return context;
};
