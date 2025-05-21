#!/bin/bash

# Start the development environment for Digi-Persona

# Start backend API server in one terminal
echo "Starting backend API server..."
gnome-terminal --tab --title="Backend API" -- bash -c "cd $(pwd) && ./scripts/run.sh --host=0.0.0.0 --port=8000; exec bash" || \
xterm -T "Backend API" -e "cd $(pwd) && ./scripts/run.sh --host=0.0.0.0 --port=8000; exec bash" || \
open -a Terminal.app "$(pwd)/scripts/run.sh --host=0.0.0.0 --port=8000" || \
echo "Cannot open a new terminal window. Please run the backend manually with './scripts/run.sh'"

# Wait for the backend to start
echo "Waiting for backend to initialize..."
sleep 3

# Start frontend in another terminal
echo "Starting frontend development server..."
gnome-terminal --tab --title="Frontend" -- bash -c "cd $(pwd)/frontend && VITE_API_URL=/api/v1 npm run dev; exec bash" || \
xterm -T "Frontend" -e "cd $(pwd)/frontend && VITE_API_URL=/api/v1 npm run dev; exec bash" || \
open -a Terminal.app "cd $(pwd)/frontend && VITE_API_URL=/api/v1 npm run dev" || \
echo "Cannot open a new terminal window. Please run the frontend manually with 'cd frontend && VITE_API_URL=/api/v1 npm run dev'"

echo "Development environment started!"
echo "Backend API: http://localhost:8000"
echo "Frontend: http://localhost:5173"
