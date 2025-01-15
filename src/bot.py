import logging
import os
import sys
import traceback

from botbuilder.core import MemoryStorage, TurnContext, ConversationState
from teams import Application, ApplicationOptions, TeamsAdapter
from teams.ai import AIOptions
from teams.ai.models import AzureOpenAIModelOptions, OpenAIModel
from teams.ai.planners import ActionPlanner, ActionPlannerOptions
from teams.ai.prompts import PromptManager, PromptManagerOptions
from teams.state import TurnState

from .config import Config

from .pii_det import remove_sensitive_info
from .rag_index import retrieval_index
from .file_upload import on_message_activity
import chromadb
from .rag_pdf import build_vector_store, retrieval_file

config = Config()

# Create AI components
model: OpenAIModel

model = OpenAIModel(
    AzureOpenAIModelOptions(
        api_key=config.AZURE_OPENAI_API_KEY,
        default_model=config.AZURE_OPENAI_MODEL_DEPLOYMENT_NAME,
        endpoint=config.AZURE_OPENAI_ENDPOINT,
        api_version=config.AZURE_OPENAI_VERSION
    )
)
    
prompts = PromptManager(PromptManagerOptions(prompts_folder=f"{os.getcwd()}/src/prompts"))

planner = ActionPlanner(
    ActionPlannerOptions(model=model, prompts=prompts, default_prompt="chat")
)

# Define storage and application
storage = MemoryStorage()
conversation_state = ConversationState(storage)
upload_file_state = conversation_state.create_property("file_uploaded")

bot_app = Application[TurnState](
    ApplicationOptions(
        bot_app_id=config.APP_ID,
        storage=storage,
        adapter=TeamsAdapter(config),
        ai=AIOptions(planner=planner),
    )
)

# Add a ChromaDB client
try:
    client = chromadb.Client()
    collection = client.get_or_create_collection("my_collection")
except:
    raise Exception("Failed to create a chromadb client.")

async def RAG(query: str, kind: str):
    # 1st step -- Remove PII from query
    query_without_pii = await remove_sensitive_info(query)
    # 2nd step -- Retrieve docs
    if kind=="index":
        docs = await retrieval_index(query_without_pii)
        # 3rd step for Index -- Include the docs in the system prompt
        try:
            with open(os.path.join(os.getcwd(), "src", "prompts", "chat", "skprompt.txt"), "a", encoding='utf-8') as f:
                f.write(docs)
        except:
            raise Exception("Couldn't change the system prompt.")
    elif kind=="user":
        docs = await retrieval_file(query_without_pii, collection)
        # 3rd step for uploaded file -- Append to the query
        query_without_pii = docs + "\n\n" + "Main question: " + query_without_pii
    # 4th step -- Return the modified query
    return query_without_pii

@bot_app.conversation_update("membersAdded")
async def on_members_added(context: TurnContext, state: TurnState):
    await context.send_activity("How can I help you today?")

@bot_app.before_turn
async def before_turn(context: TurnContext, state: TurnState):
    # Handling uploaded file
    try:
        docs = await on_message_activity(context, state) # Check for any uploaded doc
    except:
        raise Exception("Error in handling user message or uploaded file.")
    if docs:
        await context.send_activity("Download complete")
        try:
            # Storing the uploaded file in the chromadb client
            docs_str, embeddings = await build_vector_store(docs)
            ids = [f"id{i+1}" for i in range(len(docs_str))] # STILL NEEDS HANDLING OF MULTIPLE PDFS
            collection.upsert(ids=ids, documents=docs_str, embeddings=embeddings)
        except:
            raise Exception("Couldn't create a vector db from uploaded file.")
        # Set the value of whether we have encountered any uploaded file to true
        await upload_file_state.set(context, True)
        await conversation_state.save_changes(context)
        await context.send_activity("Stored in local memory. Now you can chat with your uploaded file.")
    # Preparing to generate the response
    if state.temp.input is not None:
        # Retrieve file URL from conversation state
        file_uploaded = await upload_file_state.get(context)
        if file_uploaded:
            new_query = await RAG(state.temp.input, "user")
            state.temp.input = new_query
        else:
            new_query = await RAG(state.temp.input, "index")
            state.temp.input = new_query
    return True

@bot_app.after_turn
async def after_turn(context: TurnContext, state: TurnState):
    try:
        with open(os.path.join(os.getcwd(), "src", "prompts", "chat", "skprompt.txt"), "w") as f1:
            with open(os.path.join(os.getcwd(), "src", "prompts", "chat", "temp_prompt.txt"), "r") as f2:
                f1.write(f2.read())        
    except:
        raise Exception("System prompt didn't revert back.")

@bot_app.error
async def on_error(context: TurnContext, error: Exception):
    # This check writes out errors to console log .vs. app insights.
    # NOTE: In production environment, you should consider logging this to Azure
    #       application insights.
    try:
        with open(os.path.join(os.getcwd(), "src", "prompts", "chat", "skprompt.txt"), "w") as f1:
            with open(os.path.join(os.getcwd(), "src", "prompts", "chat", "temp_prompt.txt"), "r") as f2:
                f1.write(f2.read())        
    except:
        raise Exception("System prompt didn't revert back.")
    
    logging.info(f"\n [on_turn_error] unhandled error: {error}", file=sys.stderr)
    traceback.print_exc()

    # Send a message to the user
    await context.send_activity(f"The bot encountered an error or bug.\n\n{error}")