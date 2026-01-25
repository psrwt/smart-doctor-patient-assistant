import asyncio
import os
from app.mcp_server.tools.notify_on_slack import notify_on_slack

async def test_slack_tool_call():
    print("🧪 Starting MCP Slack Tool Integration Test...")
    
    # 1. Setup test data (Simulating what the LLM would generate)
    doctor_email = "praveensingh.connect@gmail.com"
    
    # We use Markdown for the content to take advantage of Slack's 'blocks'
    report_content = (
        "*here is you summary report*\n"
        "------------------------------------------\n"
        "• *Patient:* John Doe\n"
        "  - Time: 10:30 AM\n"
        "  - Symptoms: Persistent cough and mild fever\n"
        "• *Patient:* Jane Smith\n"
        "  - Time: 02:00 PM\n"
        "  - Symptoms: Follow-up on post-surgery recovery\n"
        "\n"
        "✅ _Total: 2 appointments scheduled._"
    )

    print(f"📡 Sending report to: {doctor_email}")

    # 2. Call the service function
    # In main.py, your tool calls 'send_slack_report(doctor_email, content)'
    result = notify_on_slack(doctor_email, report_content)

    # # 3. Output results
    # if result["status"] == "success":
    #     print("✅ SUCCESS: The message should now be visible in your Slack DM!")
    # else:
    #     print(f"❌ FAILED: {result['message']}")

if __name__ == "__main__":
    # Ensure your environment variable is set in the terminal before running
    # if not os.getenv("SLACK_BOT_TOKEN"):
    #     print("⚠️  Warning: SLACK_BOT_TOKEN is not set in environment.")
    
    asyncio.run(test_slack_tool_call())