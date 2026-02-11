import os

# Disable OpenAI tracing (not compatible with OpenRouter)
os.environ["OPENAI_AGENTS_DISABLE_TRACING"] = "1"

from agents import Agent, Runner
from agents.mcp import MCPServerStdio, MCPServer
from agents.models.openai_chatcompletions import OpenAIChatCompletionsModel
from openai import AsyncOpenAI
from openai.types.responses import ResponseTextDeltaEvent
import asyncio
from dotenv import load_dotenv

load_dotenv()

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
        params={"command": "uv", "args": ["run", "mcp-server/yt-mcp.py"]},
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
        user_input = input("User: ").strip()

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
                        if tool_name == "fetch_video_transcript":
                            print("\n-- Fetching transcript...")
                        elif tool_name == "fetch_intstructions":
                            print("\n-- Fetching instructions...")
                        else:
                            print(f"\n-- Calling {tool_name}...")
                    elif event.item.type == "tool_call_output_item":
                        print("-- Done.")

            # Use the SDK's built-in method to get proper conversation history
            input_items = result.to_input_list()

            print("\n")
        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"\n[Error] {e}\nPlease try again.\n")


if __name__ == "__main__":
    asyncio.run(main())
