from typing import Annotated
from semantic_kernel.functions import kernel_function
from browser_automation_actions import BrowserAutomationActions

class BrowserInteractionPlugin:

    @property
    def description(self) -> str:
        return "Provides actions to perform on a browser."
    
    def __init__(self,headless: bool = False):
        self.headless = headless
        print("Initializing BrowserInteractionPlugin")
        self.browser_automation = BrowserAutomationActions(headless=self.headless)
    
    @kernel_function(description="Navigate to a URL")
    async def navigate_to_url(
        self, url: Annotated[str, "The URL to navigate to."]
    ) -> Annotated[bool, "Whether the action was successfully performed."]:
        print("Function called: navigate_to_url with key:", url)
        result = await self.browser_automation.start()
        if result:
            result = await self.browser_automation.navigate(url)
        return result
  
    @kernel_function(description="Press a specific key from the keyboard.")
    async def press_key(
        self, key: Annotated[str, "The destination to check availability for."]
    ) -> Annotated[bool, "Whether the action was successfully performed."]:
        print("Function called: press_key with key:", key)
        return await self.browser_automation.press_key(key)
    
    @kernel_function(description="Type a string into the browser.")
    async def type_string(
        self, string: Annotated[str, "The string to type."]
    ) -> Annotated[bool, "Whether the action was successfully performed."]:
        print("Function called: type_string with key:", string)
        return await self.browser_automation.type_text(string)

    @kernel_function(description="Find a clickable element on the page with given text and click it.")
    async def find_and_click(
        self, text: Annotated[str, "The text that the clickable element contains."]
    ) -> Annotated[bool, "Whether the action was successfully performed."]:
        print("Function called: find_and_click with key:", text)
        return await self.browser_automation._smart_click(text)

    @kernel_function(description="Find an input field on the page with given name or placeholder text and fill it with the given text.")
    def find_and_fill(
        self, 
        field: Annotated[str, "The name or placeholder text of the field where the text needs to be filled"],
        text: Annotated[str, "The text that needs to be filled"]
    ) -> Annotated[bool, "Whether the action was successfully performed."]:
        print(f"Function called: find_and_fill with field: {field}")
        return self.browser_automation._smart_fill(field, text)