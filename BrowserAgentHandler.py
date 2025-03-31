from azure.ai.inference.aio import ChatCompletionsClient
from semantic_kernel.connectors.ai.azure_ai_inference import AzureAIInferenceChatCompletion
from azure.core.credentials import AzureKeyCredential
from semantic_kernel.connectors.ai import FunctionChoiceBehavior
from semantic_kernel.functions import KernelArguments
from semantic_kernel.contents.chat_history import ChatHistory
from semantic_kernel.connectors.ai.prompt_execution_settings import PromptExecutionSettings
from semantic_kernel.kernel import Kernel
from semantic_kernel.contents import ChatHistory
import os
from dotenv import load_dotenv, find_dotenv
from browser_interaction_plugin import BrowserInteractionPlugin
from credentials_plugin import CredentialExtractionPlugin
from system_instructions import SYSTEM_INSTRUCTIONS


class BrowserAgentHandler:

    def __init__(self, headless: bool):
        self.headless = headless
        self.fetch_keys()
        self.initialize()

    def fetch_keys(self):
        dotenv_path = find_dotenv()
        load_dotenv(dotenv_path)

        self.KEY = os.environ.get('OPEN_AI_AZURE_KEY')
        self.endpoint = os.environ.get('OPEN_AI_AZURE_ENDPOINT')
        self.model_name = "gpt-4o"

    def initialize(self):
        self.chat_completion_service = AzureAIInferenceChatCompletion(
            ai_model_id=self.model_name,
            client=ChatCompletionsClient(
                endpoint=self.endpoint,
                credential=AzureKeyCredential(self.KEY),
                max_tokens=2500,
                temperature = 0
            )
        )
        
        self.kernel = Kernel()
        self.kernel.add_service(self.chat_completion_service)
        self.kernel.add_plugin(BrowserInteractionPlugin(headless = self.headless), plugin_name="BrowserInteractionPlugin")
        self.kernel.add_plugin(CredentialExtractionPlugin(), plugin_name="CredentialExtractionPlugin")
        
        self.history = ChatHistory()
        self.history.add_system_message(SYSTEM_INSTRUCTIONS)
        
    async def interact(self, query):
        arguments = KernelArguments(
            settings=PromptExecutionSettings(
                function_choice_behavior=FunctionChoiceBehavior.Auto(),
                parallel_tool_calls=False  # disable parallel/concurrent execution
            ),
            chat_history=self.history
        )

        result = await self.kernel.invoke_prompt(query, arguments=arguments)
        print(f"WebMancer:> {result}")

        self.history.add_message({
        "role": "user",
        "content": query
        })
        self.history.add_message({
        "role": "assistant",
        "content": str(result)
        })

        return self.history

