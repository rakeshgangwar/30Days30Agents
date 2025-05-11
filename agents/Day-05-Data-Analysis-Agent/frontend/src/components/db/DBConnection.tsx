import React, { useState } from 'react';
import {
  Box,
  Button,
  Card,
  CardContent,
  CircularProgress,
  FormControl,
  FormHelperText,
  InputLabel,
  MenuItem,
  Select,
  TextField,
  Typography,
  Alert,
  Grid
} from '@mui/material';
import { useAppContext } from '../../contexts/AppContext';
import api from '../../services/api';

const DBConnection: React.FC = () => {
  const { state, dispatch } = useAppContext();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Form state
  const [dbType, setDbType] = useState<string>('sqlite');
  const [dbPath, setDbPath] = useState<string>('test_data.db');
  const [host, setHost] = useState<string>('localhost');
  const [port, setPort] = useState<string>('5432');
  const [database, setDatabase] = useState<string>('');
  const [user, setUser] = useState<string>('');
  const [password, setPassword] = useState<string>('');

  const handleDbTypeChange = (event: any) => {
    setDbType(event.target.value);
  };

  const handleConnect = async () => {
    setLoading(true);
    setError(null);

    try {
      // Prepare connection parameters based on database type
      const connectionParams = dbType === 'sqlite'
        ? { db_path: dbPath }
        : { host, port, database, user, password };

      const response = await api.connectToDatabase({
        db_type: dbType,
        connection_params: connectionParams
      });

      const data = response.data;

      if (data.success) {
        dispatch({
          type: 'SET_DB_CONNECTION',
          payload: {
            connectionId: `${dbType}_${Date.now()}`, // Generate a simple ID
            dbType,
            tables: data.tables || [],
            connected: true
          }
        });
      } else {
        setError(data.error || 'Failed to connect to database');
      }
    } catch (err) {
      console.error('Error connecting to database:', err);
      setError('Error connecting to database. Please check your connection details.');
    } finally {
      setLoading(false);
    }
  };

  const handleDisconnect = () => {
    dispatch({ type: 'RESET_DB_CONNECTION' });
    setError(null);
  };

  return (
    <Card variant="outlined" sx={{ mb: 3 }}>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          Database Connection
        </Typography>

        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        {state.database.connected ? (
          <Box>
            <Alert severity="success" sx={{ mb: 2 }}>
              Connected to {state.database.dbType} database
            </Alert>

            {state.database.tables.length > 0 && (
              <Box sx={{ mb: 2 }}>
                <Typography variant="subtitle2" gutterBottom>
                  Available Tables:
                </Typography>
                <Typography variant="body2">
                  {state.database.tables.join(', ')}
                </Typography>
              </Box>
            )}

            <Button
              variant="outlined"
              color="primary"
              onClick={handleDisconnect}
            >
              Disconnect
            </Button>
          </Box>
        ) : (
          <Box component="form">
            <FormControl fullWidth margin="normal">
              <InputLabel id="db-type-label">Database Type</InputLabel>
              <Select
                labelId="db-type-label"
                value={dbType}
                label="Database Type"
                onChange={handleDbTypeChange}
              >
                <MenuItem value="sqlite">SQLite</MenuItem>
                <MenuItem value="postgresql">PostgreSQL</MenuItem>
              </Select>
            </FormControl>

            {dbType === 'sqlite' ? (
              <TextField
                fullWidth
                margin="normal"
                label="Database Path"
                value={dbPath}
                onChange={(e) => setDbPath(e.target.value)}
                helperText="Path to SQLite database file"
              />
            ) : (
              <Grid container spacing={2}>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    margin="normal"
                    label="Host"
                    value={host}
                    onChange={(e) => setHost(e.target.value)}
                  />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    margin="normal"
                    label="Port"
                    value={port}
                    onChange={(e) => setPort(e.target.value)}
                  />
                </Grid>
                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    margin="normal"
                    label="Database Name"
                    value={database}
                    onChange={(e) => setDatabase(e.target.value)}
                  />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    margin="normal"
                    label="Username"
                    value={user}
                    onChange={(e) => setUser(e.target.value)}
                  />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    margin="normal"
                    label="Password"
                    type="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                  />
                </Grid>
              </Grid>
            )}

            <Box sx={{ mt: 2 }}>
              <Button
                variant="contained"
                color="primary"
                onClick={handleConnect}
                disabled={loading}
                startIcon={loading ? <CircularProgress size={20} /> : null}
              >
                Connect
              </Button>
            </Box>
          </Box>
        )}
      </CardContent>
    </Card>
  );
};

export default DBConnection;
