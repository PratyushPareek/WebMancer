
from typing import Annotated
from semantic_kernel.functions import kernel_function
import os 

class CredentialExtractionPlugin:

    @property
    def description(self) -> str:
        return "Provides the model with the credentials for the browser."
    
    @kernel_function(description="Provides the model with the github username.")
    def github_username(self) -> Annotated[str, "Github username"]:
        print("Function called: github_username")
        return "pratyushpareek26@gmail.com"
    
    @kernel_function(description="Provides the model with the github password.")
    def github_password(self) -> Annotated[str, "Github password"]:
        print("Function called: github_password")
        password = os.environ.get('GITHUB_PASSWORD')
        print("password retreived")
        return password