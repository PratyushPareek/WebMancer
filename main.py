import asyncio
from BrowserAgentHandler import BrowserAgentHandler

TASKS = [
    "Go to github.com. Click on Sign In. Fill in username and Password in their respective input fields after extracting them. Click on Sign in. ",
    "Click search. Type 'playwright' in the input field. Once filled, Press Enter key on keyboard. Then Click on playwright-python"
]


async def run(headless: bool = False, tasks: list[str] = TASKS) -> bool:

    agent = BrowserAgentHandler(headless=headless)

    for i,instruction in enumerate(tasks):
        print("INSTRUCTION ", i, ": ", instruction)
        history = await agent.interact(instruction)
        print("EXECUTED INSTRUCTION ", i)

    print("HISTORY: ", history)


if __name__ == "__main__":
    asyncio.run(run())