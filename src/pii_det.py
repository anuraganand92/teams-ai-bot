from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential
from .config import Config

config = Config()

# Authenticate the client using key and endpoint 
client = TextAnalyticsClient(endpoint=config.LANGUAGE_ENDPOINT, 
                             credential=AzureKeyCredential(config.LANGUAGE_KEY),
                             minimumPrecision=0.6
                            )

async def remove_sensitive_info(prompt: str):    
    allowed_categories = ['PersonType', 'DateTime', 'Quantity', 'Organization']

    # Detecting sensitive information (PII) from text 
    response = client.recognize_pii_entities([prompt], language="en")

    for doc in response: # Looping over 1 element list
        if doc.is_error:
            return prompt
        else:
            if len(doc.entities)==0:
                return prompt
            else:
                idx = 0
                new_prompt = ""
                for entity in doc.entities:
                    if entity.category not in allowed_categories:
                        new_prompt += prompt[idx:entity.offset] + '[.]'
                        idx = entity.offset + entity.length
                new_prompt += prompt[idx:]
                return new_prompt
