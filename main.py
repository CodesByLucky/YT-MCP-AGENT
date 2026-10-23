"""YouTube video agent: OpenAI Agents SDK + an MCP tool server, via OpenRouter."""
import asyncio
import os
import sys
from pathlib import Path

# Disable OpenAI tracing (not compatible with OpenRouter)
os.environ["OPENAI_AGENTS_DISABLE_TRACING"] = "1"

from agents import Agent, Runner
from agents.mcp import MCPServer, MCPServerStdio
from agents.models.openai_chatcompletions import OpenAIChatCompletionsModel
from dotenv import load_dotenv
from openai import AsyncOpenAI
from openai.types.responses import ResponseTextDeltaEvent

load_dotenv()

ROOT = Path(__file__).resolve().parent
TOOL_STATUS = {
    "fetch_video_transcript": "Fetching transcript...",
    "fetch_instructions": "Fetching instructions...",
}

# --- Configuration ---
MODEL = os.getenv("OPENAI_MODEL", "meta-llama/llama-3.3-70b-instruct:free")

client = AsyncOpenAI(
    base_url=os.getenv("OPENAI_BASE_URL", "https://openrouter.ai/api/v1"),
    api_key=os.getenv("OPENAI_API_KEY"),
    default_headers={
        "HTTP-Referer": "http://localhost",
        "X-Title": "YT MCP Agent",
    },
)

model = OpenAIChatCompletionsModel(model=MODEL, openai_client=client)


# --- Agent ---
async def main():
    async with MCPServerStdio(
        name="YouTube MCP Server",
        params={"command": "uv", "args": ["run", "mcp-server/yt-mcp.py"], "cwd": str(ROOT)},
    ) as server:
        await run(server)


async def run(mcp_server: MCPServer):
    prompt_result = await mcp_server.get_prompt("system_prompt")
    instructions = prompt_result.messages[0].content.text

    agent = Agent(
        name="YouTube Video Agent",
        instructions=instructions,
        mcp_servers=[mcp_server],
        model=model,
    )

    # Let the SDK manage conversation history
    input_items = []

    print("=== YouTube Agent ===")
    print(f"Model: {MODEL}")
    print("Type 'exit' to quit\n")

    while True:
        try:
            user_input = input("User: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        if user_input.lower() in ["exit", "quit", "bye"]:
            print("\nGoodbye!")
            break

        if not user_input:
            continue

        input_items.append({"content": user_input, "role": "user"})

        try:
            result = Runner.run_streamed(agent, input=input_items)
            print("\nAgent: ", end="", flush=True)

            async for event in result.stream_events():
                if event.type == "raw_response_event" and isinstance(
                    event.data, ResponseTextDeltaEvent
                ):
                    print(event.data.delta, end="", flush=True)
                elif event.type == "run_item_stream_event":
                    if event.item.type == "tool_call_item":
                        tool_name = event.item.raw_item.name
                        print(f"\n-- {TOOL_STATUS.get(tool_name, f'Calling {tool_name}...')}")
                    elif event.item.type == "tool_call_output_item":
                        print("-- Done.")

            # Use the SDK's built-in method to get proper conversation history
            input_items = result.to_input_list()

            print("\n")
        except Exception as e:
            input_items.pop()  # drop the failed turn so a retry starts clean
            print(f"\n[Error] {e}\nPlease try again.\n")


if __name__ == "__main__":
    if not os.getenv("OPENAI_API_KEY"):
        sys.exit("OPENAI_API_KEY is not set. Copy .env.example to .env and add your OpenRouter key.")
    asyncio.run(main())
