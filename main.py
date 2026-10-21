
# ============================================================
# IMPORTS
# ============================================================

# Environment variables aur Render ke PORT ko access karne ke liye
import os

# JSON data ko readable string mein convert karne ke liye
import json

# Expense add karte waqt date aur time record karne ke liye
from datetime import datetime, timezone

# FastMCP framework se MCP server create karne ke liye
from fastmcp import FastMCP


# ============================================================
# MCP SERVER INITIALIZATION
# ============================================================

# Expense Tracker ke naam se MCP server create karna
mcp = FastMCP("Expense Tracker MCP Server")


# ============================================================
# IN-MEMORY EXPENSE STORAGE
# ============================================================

# Filhaal expenses memory mein store honge.
# IMPORTANT: Server restart hone par ye data reset ho jayega.
expenses = []

# Har expense ko unique ID dene ke liye counter
next_expense_id = 1


# ============================================================
# TOOL 1: ADD AN EXPENSE
# ============================================================

# Function ko MCP tool ke roop mein register karna
@mcp.tool
def add_expense(
    amount: float,
    category: str,
    description: str
) -> str:
    """
    Naya expense record karta hai.

    Args:
        amount: Expense ki amount; positive honi chahiye.
        category: Expense ki category, jaise Food ya Travel.
        description: Expense ka short description.

    Returns:
        Added expense ki details JSON format mein.
    """

    # Global ID counter ko update karne ki permission lena
    global next_expense_id

    # Invalid ya zero amount ko reject karna
    if amount <= 0:
        return json.dumps({
            "error": "Expense amount must be greater than zero."
        })

    # Category aur description empty nahi hone chahiye
    if not category.strip() or not description.strip():
        return json.dumps({
            "error": "Category and description cannot be empty."
        })

    # Naye expense ka record create karna
    expense = {
        "id": next_expense_id,
        "amount": round(amount, 2),
        "category": category.strip().title(),
        "description": description.strip(),
        "created_at": datetime.now(timezone.utc).isoformat()
    }

    # Expense ko list mein save karna
    expenses.append(expense)

    # Agle expense ke liye ID increment karna
    next_expense_id += 1

    # Added expense ki details return karna
    return json.dumps({
        "message": "Expense added successfully.",
        "expense": expense
    }, indent=2)


# ============================================================
# TOOL 2: VIEW ALL EXPENSES
# ============================================================

@mcp.tool
def get_expenses() -> str:
    """
    Saare recorded expenses return karta hai.
    """

    # Agar abhi tak koi expense add nahi hua
    if not expenses:
        return json.dumps({
            "message": "No expenses recorded yet.",
            "expenses": []
        }, indent=2)

    # Saare expenses ko JSON format mein return karna
    return json.dumps({
        "total_records": len(expenses),
        "expenses": expenses
    }, indent=2)


# ============================================================
# TOOL 3: CALCULATE TOTAL SPENDING
# ============================================================

@mcp.tool
def get_total_spending() -> str:
    """
    Saare expenses ka total calculate karta hai.
    """

    # Har expense ki amount ko add karna
    total = sum(expense["amount"] for expense in expenses)

    # Total aur record count return karna
    return json.dumps({
        "total_spending": round(total, 2),
        "currency": "INR",
        "total_records": len(expenses)
    }, indent=2)


# ============================================================
# TOOL 4: CATEGORY-WISE EXPENSE SUMMARY
# ============================================================

@mcp.tool
def get_category_summary() -> str:
    """
    Har category mein kitna paisa kharch hua,
    uska summary return karta hai.
    """

    # Har category ka total store karne ke liye dictionary
    category_totals = {}

    # Saare expenses ko category ke hisaab se group karna
    for expense in expenses:
        category = expense["category"]

        # Category pehli baar aaye toh initial total zero rakhna
        if category not in category_totals:
            category_totals[category] = 0.0

        # Expense amount ko uski category ke total mein add karna
        category_totals[category] += expense["amount"]

    # Floating-point rounding errors ko kam karne ke liye
    # final totals ko 2 decimal places tak round karna
    category_totals = {
        category: round(total, 2)
        for category, total in category_totals.items()
    }

    # Category-wise result return karna
    return json.dumps({
        "currency": "INR",
        "category_summary": category_totals
    }, indent=2)


# ============================================================
# RESOURCE: SERVER INFORMATION
# ============================================================

# Is URI se MCP client server ki information read kar sakta hai
@mcp.resource("info://server")
def server_info() -> str:
    """
    Expense Tracker server ki basic information return karta hai.
    """

    # Application ki details define karna
    info = {
        "name": "Expense Tracker MCP Server",
        "version": "1.0.0",
        "description": (
            "MCP server for recording expenses, "
            "calculating spending, and viewing category summaries."
        ),
        "currency": "INR",
        "storage": "In-memory; data resets when server restarts."
    }

    # Dictionary ko readable JSON string mein convert karna
    return json.dumps(info, indent=2)


# ============================================================
# REMOTE SERVER STARTUP — RENDER READY
# ============================================================

if __name__ == "__main__":

    # Render PORT environment variable provide karta hai.
    # Local testing ke liye default port 8000 use hoga.
    port = int(os.environ.get("PORT", 8000))

    # HTTP transport par server start karna.
    # 0.0.0.0 Render ke network se incoming requests accept karta hai.
    mcp.run(
    transport="http",
    host="0.0.0.0",
    port=port,
    stateless_http=True  # Session ID ke bina HTTP requests allow karega
)
