#!/bin/bash
echo "Starting MOSAIC Edge + Swarm Simulator"
echo "======================================="

cd /home/leopardtech/Desktop/mosaic-edge

# Start main.py in background
echo "Starting main.py (node-01)..."
python3 main.py &
MAIN_PID=$!
echo "main.py started PID: $MAIN_PID"

# Wait 5 seconds for main to initialize
sleep 5

# Start swarm simulator in background
echo "Starting swarm_simulator.py (nodes 02 03 04)..."
python3 swarm_simulator.py &
SIM_PID=$!
echo "simulator started PID: $SIM_PID"

echo ""
echo "Both running"
echo "main.py PID: $MAIN_PID"
echo "simulator PID: $SIM_PID"
echo ""
echo "Press Ctrl+C to stop both"

# Wait for either to exit
wait $MAIN_PID $SIM_PID
