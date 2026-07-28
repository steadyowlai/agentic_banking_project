"""
MCP Resources: Policy Documents

Exposes banking policy documents as MCP resources.
Client llms can read these to understand lending policies.

Resources are READ-ONLY data exposed via URIs:
- policy://retail - Retail customer lending policy
- policy://corporate - Corporate customer lending policy

"""

from utils.file_utils import get_policy_content
# mcp_server/utils/file_utils.py contains the get_policy_content function 
# that reads policy files from the data/policies directory.

def setup_policy_resources(mcp):
    """
    Register policy resources with the FastMCP server.
    
    Args:
        mcp: FastMCP server instance
    """
    
    @mcp.resource("policy://retail")
    def get_retail_policy() -> str:
        """Retail customer lending policy - pre-approval limits and requirements"""
        content = get_policy_content('retail')
        if content is None:
            raise ValueError("Retail policy not found")
        return content
    
    @mcp.resource("policy://corporate")
    def get_corporate_policy() -> str:
        """Corporate customer lending policy - pre-approval limits and requirements"""
        content = get_policy_content('corporate')
        if content is None:
            raise ValueError("Corporate policy not found")
        return content
