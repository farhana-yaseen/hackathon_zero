@echo off
REM Start all 4 MCP servers for Gold Tier
REM Each server runs in a separate window

echo Starting all MCP servers...
echo.

set VAULT_PATH=D:\hackthon\hackathon_zero\AI_Employee_Vault

REM Start Main MCP Server (port 8080)
start "Main MCP Server (8080)" cmd /k "cd /d %VAULT_PATH%\scripts && python mcp_server.py --vault-path %VAULT_PATH% --port 8080"
timeout /t 2 /nobreak >nul

REM Start ERP/Accounting MCP Server (port 8081)
start "ERP MCP Server (8081)" cmd /k "cd /d %VAULT_PATH%\scripts && python mcp_server_erp.py --vault-path %VAULT_PATH% --port 8081"
timeout /t 2 /nobreak >nul

REM Start Social Media MCP Server (port 8082)
start "Social MCP Server (8082)" cmd /k "cd /d %VAULT_PATH%\scripts && python mcp_server_social.py --vault-path %VAULT_PATH% --port 8082"
timeout /t 2 /nobreak >nul

REM Start Communications MCP Server (port 8083)
start "Comms MCP Server (8083)" cmd /k "cd /d %VAULT_PATH%\scripts && python mcp_server_comms.py --vault-path %VAULT_PATH% --port 8083"

echo.
echo All 4 MCP servers started in separate windows
echo.
echo Health check URLs:
echo   http://localhost:8080/mcp/health - Main MCP Server
echo   http://localhost:8081/mcp/health - ERP/Accounting Server
echo   http://localhost:8082/mcp/health - Social Media Server
echo   http://localhost:8083/mcp/health - Communications Server
echo.
echo Press any key to exit...
pause >nul
