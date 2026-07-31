"""
Loan Database Tools

Exposes database access to the LLM. Enforces Zero Trust Architecture by 
verifying JWT tokens before allowing database queries.
"""

import sys
import os

from fastmcp import Context

#path resolution to access utils
TOOLS_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.dirname(TOOLS_DIR)
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from utils.database import get_loans_by_user_id, get_loan_by_id
from utils.auth_utils import verify_and_decode_token


def setup_loan_tools(mcp):
    """Register loan tools with the FastMCP server instance."""
    
    @mcp.tool()
    def get_my_loans(ctx: Context) -> str:
        """
        Fetches the active and pending loans for the currently authenticated user.
        Requires a valid Bearer token in the authorization header.
        """
        #extract headers from the fastmcp Context
        headers = getattr(ctx.session, "headers", {}) if hasattr(ctx, "session") else {}
        auth_header = headers.get("authorization", "")
        
        #zero trust, verify token
        payload = verify_and_decode_token(auth_header)
        
        if not payload:
            return "AUTH_ERROR: Invalid, expired, or missing Bearer token. Please authenticate."
            
        user_id = payload.get("user_id")
        
        #fetch data restricted only to this user_id
        loans = get_loans_by_user_id(user_id)
        
        if not loans:
            return "No loans found for your account."
            
        #format the response nicely for the LLM
        response = f"Found {len(loans)} loans for user {user_id}:\n\n"
        for loan in loans:
            response += f"- Loan ID: {loan['loan_id']}\n"
            response += f"  Status: {loan['status']}\n"
            response += f"  Balance: ${loan['balance']:,.2f}\n"
            response += f"  Interest Rate: {loan['interest_rate']}%\n"
            response += f"  Maturity Date: {loan['maturity_date']}\n\n"
            
        return response

    @mcp.tool()
    def get_loan_details(loan_id: str, ctx: Context) -> str:
        """
        Fetches detailed information for a specific loan ID.
        Only returns data if the authenticated user owns the loan.
        """
        #extract headers and verify token
        headers = getattr(ctx.session, "headers", {}) if hasattr(ctx, "session") else {}
        auth_header = headers.get("authorization", "")
        
        payload = verify_and_decode_token(auth_header)
        if not payload:
            return "AUTH_ERROR: Invalid, expired, or missing Bearer token."
            
        user_id = payload.get("user_id")
        
        #fetch loan from database
        loan = get_loan_by_id(loan_id)
        
        # SECURITY CHECK: Prevent IDOR and Enumeration
        # If the loan doesn't exist, OR if it belongs to someone else, 
        # return the exact same message so malicious users can't guess valid loan IDs.
        if not loan or loan["user_id"] != user_id:
            return f"Loan {loan_id} not found in your account."
            
        #format response
        response = f"Loan Details for {loan_id}:\n"
        response += f"- Status: {loan['status']}\n"
        response += f"- Balance: ${loan['balance']:,.2f}\n"
        response += f"- Interest Rate: {loan['interest_rate']}%\n"
        response += f"- Maturity Date: {loan['maturity_date']}\n"
        response += f"- Product Type: {loan['customer_type']}\n"
        
        return response
