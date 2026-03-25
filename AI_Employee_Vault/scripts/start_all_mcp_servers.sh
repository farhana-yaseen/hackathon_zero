#!/bin/bash
# Start all 4 MCP servers for Gold Tier
# Each server runs in the background

VAULT_PATH="$(cd "$(dirname "$0")/.." && pwd)"
SCRIPTS_DIR="$VAULT_PATH/scripts"

echo "Starting all MCP servers..."
echo ""

# Start Main MCP Server (port 8080)
echo "Starting Main MCP Server on port 8080..."
cd "$SCRIPTS_DIR"
python3 mcp_server.py --vault-path "$VAULT_PATH" --port 8080 > "$VAULT_PATH/Logs/mcp_main.log" 2>&1 &
MCP_MAIN_PID=$!
sleep 2

# Start ERP/Accounting MCP Server (port 8081)
echo "Starting ERP/Accounting MCP Server on port 8081..."
python3 mcp_server_erp.py --vault-path "$VAULT_PATH" --port 8081 > "$VAULT_PATH/Logs/mcp_erp.log" 2>&1 &
MCP_ERP_PID=$!
sleep 2

# Start Social Media MCP Server (port 8082)
echo "Starting Social Media MCP Server on port 8082..."
python3 mcp_server_social.py --vault-path "$VAULT_PATH" --port 8082 > "$VAULT_PATH/Logs/mcp_social.log" 2>&1 &
MCP_SOCIAL_PID=$!
sleep 2

# Start Communications MCP Server (port 8083)
echo "Starting Communications MCP Server on port 8083..."
python3 mcp_server_comms.py --vault-path "$VAULT_PATH" --port 8083 > "$VAULT_PATH/Logs/mcp_comms.log" 2>&1 &
MCP_COMMS_PID=$!
sleep 2

echo ""
echo "All 4 MCP servers started!"
echo ""
echo "Process IDs:"
echo "  Main MCP Server:    $MCP_MAIN_PID"
echo "  ERP Server:         $MCP_ERP_PID"
echo "  Social Server:      $MCP_SOCIAL_PID"
echo "  Communications:     $MCP_COMMS_PID"
echo ""
echo "Health check URLs:"
echo "  http://localhost:8080/mcp/health - Main MCP Server"
echo "  http://localhost:8081/mcp/health - ERP/Accounting Server"
echo "  http://localhost:8082/mcp/health - Social Media Server"
echo "  http://localhost:8083/mcp/health - Communications Server"
echo ""
echo "Logs:"
echo "  $VAULT_PATH/Logs/mcp_main.log"
echo "  $VAULT_PATH/Logs/mcp_erp.log"
echo "  $VAULT_PATH/Logs/mcp_social.log"
echo "  $VAULT_PATH/Logs/mcp_comms.log"
echo ""
echo "To stop all servers:"
echo "  kill $MCP_MAIN_PID $MCP_ERP_PID $MCP_SOCIAL_PID $MCP_COMMS_PID"
echo ""

# Save PIDs to file for easy cleanup
echo "$MCP_MAIN_PID" > "$VAULT_PATH/mcp_servers.pid"
echo "$MCP_ERP_PID" >> "$VAULT_PATH/mcp_servers.pid"
echo "$MCP_SOCIAL_PID" >> "$VAULT_PATH/mcp_servers.pid"
echo "$MCP_COMMS_PID" >> "$VAULT_PATH/mcp_servers.pid"

echo "PID file saved to: $VAULT_PATH/mcp_servers.pid"
