#!/bin/bash
# Railway 啟動腳本

# 確保使用虛擬環境中的 Python
python3 -m uvicorn parser-server:app --host 0.0.0.0 --port $PORT --workers 1

