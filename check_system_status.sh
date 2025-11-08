#!/bin/bash

# System Status Checker for Heimdall Drone App
# Run this on the simulator machine (10.20.1.31) to diagnose issues

echo "============================================"
echo "🔍 Heimdall System Status Check"
echo "============================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 1. Check if backend is running
echo "1️⃣  Checking Backend Status..."
BACKEND_PID=$(ps aux | grep "[u]vicorn" | grep "main:app" | awk '{print $2}')
if [ -n "$BACKEND_PID" ]; then
    echo -e "${GREEN}✅ Backend is running${NC} (PID: $BACKEND_PID)"
else
    echo -e "${RED}❌ Backend is NOT running${NC}"
    echo "   Start with: cd ~/heimdall-app/backend && nohup python -m uvicorn main:app --host 0.0.0.0 --port 8000 > ../logs/backend.log 2>&1 &"
fi
echo ""

# 2. Check if frontend is running
echo "2️⃣  Checking Frontend Status..."
FRONTEND_PID=$(ps aux | grep "[n]pm run preview" | awk '{print $2}')
if [ -n "$FRONTEND_PID" ]; then
    echo -e "${GREEN}✅ Frontend is running${NC} (PID: $FRONTEND_PID)"
else
    echo -e "${YELLOW}⚠️  Frontend might not be running${NC}"
    echo "   Start with: cd ~/heimdall-app/frontend && npm run build && nohup npm run preview -- --host 0.0.0.0 > ../logs/frontend.log 2>&1 &"
fi
echo ""

# 3. Check if Sphinx simulator is running
echo "3️⃣  Checking Sphinx Simulator Status..."
SPHINX_PID=$(ps aux | grep -E "[s]phinx|[f]wman" | grep -v grep | awk '{print $2}')
if [ -n "$SPHINX_PID" ]; then
    echo -e "${GREEN}✅ Sphinx simulator is running${NC} (PID: $SPHINX_PID)"
else
    echo -e "${RED}❌ Sphinx simulator is NOT running${NC}"
    echo "   This is likely causing the emergency landing!"
    echo "   Start Sphinx according to your setup documentation"
fi
echo ""

# 4. Check network connectivity to Sphinx
echo "4️⃣  Checking Connectivity to Sphinx (10.202.0.1)..."
if ping -c 1 10.202.0.1 &> /dev/null; then
    echo -e "${GREEN}✅ Can ping Sphinx IP${NC} (10.202.0.1)"
else
    echo -e "${RED}❌ Cannot ping Sphinx IP${NC} (10.202.0.1)"
    echo "   Sphinx might not be running or network is not configured"
fi
echo ""

# 5. Check Olympe port (1883 - MQTT)
echo "5️⃣  Checking Olympe Port (1883)..."
if nc -z -w2 10.202.0.1 1883 2>/dev/null; then
    echo -e "${GREEN}✅ Port 1883 is open${NC} on 10.202.0.1"
else
    echo -e "${RED}❌ Port 1883 is NOT open${NC} on 10.202.0.1"
    echo "   Sphinx might not be running or Olympe is not listening"
fi
echo ""

# 6. Check backend logs for errors
echo "6️⃣  Checking Recent Backend Logs..."
if [ -f ~/heimdall-app/logs/backend.log ]; then
    echo "Last 30 lines of backend.log:"
    echo "-------------------------------------------"
    tail -30 ~/heimdall-app/logs/backend.log
    echo "-------------------------------------------"
    echo ""

    # Check for specific errors
    if grep -q "EMERGENCY LANDING" ~/heimdall-app/logs/backend.log; then
        echo -e "${RED}⚠️  EMERGENCY LANDING detected in logs!${NC}"
        echo "Last emergency landing:"
        grep -B5 "EMERGENCY LANDING" ~/heimdall-app/logs/backend.log | tail -6
        echo ""
    fi

    if grep -q "Failed to connect" ~/heimdall-app/logs/backend.log; then
        echo -e "${RED}⚠️  Connection failures detected!${NC}"
        echo "Last connection error:"
        grep "Failed to connect" ~/heimdall-app/logs/backend.log | tail -1
        echo ""
    fi
else
    echo -e "${YELLOW}⚠️  Backend log file not found${NC}"
    echo "   Expected at: ~/heimdall-app/logs/backend.log"
fi

# 7. Check environment configuration
echo "7️⃣  Checking Frontend Environment Configuration..."
if [ -f ~/heimdall-app/frontend/.env ]; then
    echo "Frontend .env file exists:"
    cat ~/heimdall-app/frontend/.env

    if grep -q "VITE_USE_REAL_API=true" ~/heimdall-app/frontend/.env; then
        echo -e "${GREEN}✅ REAL API mode enabled${NC}"
    else
        echo -e "${RED}❌ REAL API mode NOT enabled${NC}"
        echo "   Should have: VITE_USE_REAL_API=true"
    fi
else
    echo -e "${RED}❌ Frontend .env file NOT found${NC}"
    echo "   Create ~/heimdall-app/frontend/.env with VITE_USE_REAL_API=true"
fi
echo ""

# 8. Check disk space
echo "8️⃣  Checking Disk Space..."
DISK_USAGE=$(df -h ~/heimdall-app | tail -1 | awk '{print $5}' | sed 's/%//')
if [ "$DISK_USAGE" -lt 90 ]; then
    echo -e "${GREEN}✅ Disk space OK${NC} (${DISK_USAGE}% used)"
else
    echo -e "${YELLOW}⚠️  Disk space getting full${NC} (${DISK_USAGE}% used)"
fi
echo ""

# Summary
echo "============================================"
echo "📋 SUMMARY"
echo "============================================"

ISSUES=0

[ -z "$BACKEND_PID" ] && { echo -e "${RED}❌ Backend not running${NC}"; ISSUES=$((ISSUES+1)); }
[ -z "$SPHINX_PID" ] && { echo -e "${RED}❌ Sphinx not running${NC}"; ISSUES=$((ISSUES+1)); }
! ping -c 1 10.202.0.1 &> /dev/null && { echo -e "${RED}❌ Cannot reach Sphinx IP${NC}"; ISSUES=$((ISSUES+1)); }
! nc -z -w2 10.202.0.1 1883 2>/dev/null && { echo -e "${RED}❌ Olympe port closed${NC}"; ISSUES=$((ISSUES+1)); }

if [ $ISSUES -eq 0 ]; then
    echo -e "${GREEN}✅ All systems appear to be running!${NC}"
    echo ""
    echo "If you're still seeing emergency landing errors:"
    echo "  1. Check coordinates are valid (lat ~49.5-49.6, lon ~22.6-22.7)"
    echo "  2. Check altitude is reasonable (<100m)"
    echo "  3. Review full backend logs: tail -100 ~/heimdall-app/logs/backend.log"
else
    echo -e "${RED}⚠️  Found $ISSUES issue(s) - see details above${NC}"
    echo ""
    echo "Most likely cause of emergency landing:"
    if [ -z "$SPHINX_PID" ]; then
        echo -e "${RED}  → Sphinx simulator is not running${NC}"
    elif ! nc -z -w2 10.202.0.1 1883 2>/dev/null; then
        echo -e "${RED}  → Cannot connect to Olympe (port 1883)${NC}"
    elif [ -z "$BACKEND_PID" ]; then
        echo -e "${RED}  → Backend is not running${NC}"
    fi
fi

echo ""
echo "For detailed debugging, see: EMERGENCY_LANDING_DEBUG.md"
echo "============================================"
