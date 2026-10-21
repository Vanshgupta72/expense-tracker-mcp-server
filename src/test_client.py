
# Async MCP client calls ke liye
import asyncio

# FastMCP client import karna
from fastmcp import Client


# Expense Tracker ke tools test karna
async def main():

    # Local MCP server se connect karna
    async with Client("http://127.0.0.1:8000/mcp") as client:

        # Server ke saare available tools dekhna
        tools = await client.list_tools()
        print("Available tools:")
        for tool in tools:
            print("-", tool.name)

        # Pehla expense add karna
        result = await client.call_tool(
            "add_expense",
            {
                "amount": 250,
                "category": "Food",
                "description": "Lunch"
            }
        )
        print("\nAdd expense result:")
        print(result)

        # Doosra expense add karna
        result = await client.call_tool(
            "add_expense",
            {
                "amount": 120,
                "category": "Travel",
                "description": "Bus fare"
            }
        )
        print("\nSecond expense result:")
        print(result)

        # Total spending calculate karna
        result = await client.call_tool("get_total_spending", {})
        print("\nTotal spending:")
        print(result)

        # Category-wise summary check karna
        result = await client.call_tool("get_category_summary", {})
        print("\nCategory summary:")
        print(result)

        # Saare expenses dekhna
        result = await client.call_tool("get_expenses", {})
        print("\nAll expenses:")
        print(result)


# Testing function execute karna
if __name__ == "__main__":
    asyncio.run(main())
