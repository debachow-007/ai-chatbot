#!/bin/bash
# ------------------------------------
# Daily Data Refresh Job for VibesBot
# ------------------------------------

LOG_DIR="/home/debargha/Desktop/ai-chatbot/logs"
LOG_FILE="$LOG_DIR/cron_$(date +'%Y-%m-%d').log"

# Ensure log directory exists
mkdir -p "$LOG_DIR"

{
echo "==========================="
echo "VibesBot Daily Job Start"
echo "Date: $(date)"
echo "==========================="

# Activate virtual environment
echo "Activating venv..."
source /home/debargha/Desktop/ai-chatbot/venv/bin/activate

# Navigate to project
cd /home/debargha/Desktop/ai-chatbot

echo "Running crawler..."
python3 crawler/run.py

echo "Generating RAG embeddings..."
python3 run_embeddings.py

echo "Updating portfolio embeddings..."
python3 run_portfolio_embeddings.py

echo "Job completed at $(date)"
echo "=========================== "

} >> "$LOG_FILE" 2>&1
