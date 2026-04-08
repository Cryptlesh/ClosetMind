from google.adk.tools.mcp_tool.mcp_toolset import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp.client.stdio import StdioServerParameters
from app.core.settings import settings
import logging

logger = logging.getLogger(__name__)

class MCPManager:
    def __init__(self):
        # In ADK 1.28.x, we manage a list of McpToolset instances
        self.toolsets = []
        self.is_initialized = False

    async def initialize(self):
        """Initializes external MCP servers and adds them to the list of toolsets."""
        if self.is_initialized:
            return
        
        try:
            import sys
            import os
            
            # Determine the path to the mcp-toolbox executable in the same venv
            scripts_dir = os.path.dirname(sys.executable)
            mcp_toolbox_path = os.path.join(scripts_dir, "mcp-toolbox.exe")
            if not os.path.exists(mcp_toolbox_path):
                # Fallback for non-Windows if needed
                mcp_toolbox_path = os.path.join(scripts_dir, "mcp-toolbox")
            
            # 1. Register the local custom Calendar MCP using Stdio
            # We call the Python script we just created
            calendar_mcp_path = os.path.join(os.path.dirname(__file__), "calendar_mcp.py")
            workspace_params = StdioConnectionParams(
                server_params=StdioServerParameters(
                    command=sys.executable,
                    args=[calendar_mcp_path],
                    env=None
                )
            )
            self.toolsets.append(McpToolset(connection_params=workspace_params))
            
            # 2. Register the AlloyDB MCP Toolbox
            import os
            env_vars = dict(os.environ)
            if settings.MCP_TOOLBOX_AlloyDB_POSTGRES_URL:
                env_vars["DATABASE_URL"] = settings.MCP_TOOLBOX_AlloyDB_POSTGRES_URL
                env_vars["ALLOYDB_POSTGRES_URL"] = settings.MCP_TOOLBOX_AlloyDB_POSTGRES_URL
            
            toolbox_params = StdioConnectionParams(
                server_params=StdioServerParameters(
                    command=mcp_toolbox_path,
                    args=["server", "--db", "alloydb"],
                    env=env_vars
                )
            )
            self.toolsets.append(McpToolset(connection_params=toolbox_params))

            self.is_initialized = True
            logger.info(f"MCP Manager initialized with {len(self.toolsets)} toolsets.")
            
        except Exception as e:
            logger.error(f"Failed to initialize MCP servers: {e}")
            raise

mcp_manager = MCPManager()
