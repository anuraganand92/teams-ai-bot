import requests
from botbuilder.core import TurnContext
from teams.state import TurnState

from .extract_text_from_blob import extract_text

async def on_message_activity(turn_context: TurnContext, state: TurnState):

    if turn_context.activity.attachments:
        
        # Save the uploaded file in a variable
        file = turn_context.activity.attachments[0]
        if file.content_type in ["application/pdf", "text/plain"]:
            await turn_context.send_activity("Processing your uploaded file. Please wait a moment...")
            try: 
                # Get the file type and content of the uploaded file
                file_type = (file.name).split(".")[-1]
                response = requests.get(file.content_url, allow_redirects=True)
            except:
                raise Exception("Couldn't download the file from the given URL.")
        elif "image" in file.content_type:
            await turn_context.send_activity("Processing your uploaded file. Please wait a moment...")
            try:
                # Get the file type and URL
                file_type = "image"
                response = file.content_url
            except:
                raise Exception("The uploaded image's URL doesn't exist")
        elif file.content_type=="application/vnd.microsoft.teams.file.download.info":
            await turn_context.send_activity("Processing your uploaded file. Please wait a moment...")
            try:
                file_type = file.content["fileType"]
                if file_type in ["pdf", "txt"]:
                    response = requests.get(file.content["downloadUrl"], allow_redirects=True)
                elif file_type in ["png", "jpeg", "jpg", "tiff", "svg", "heic", "webp", "gif"]:
                    response = file.content["downloadUrl"]
            except:
                raise Exception("Couldn't download the uploaded file in Teams/SharePoint from the given URL.")
        else:
            return None
        docs = await extract_text(response, file_type) # Extract content
        print(docs, "\n\n")
        return docs
    else:
        return None