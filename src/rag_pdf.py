# --------------------Importing libraries-----------------------#
from teams.ai.embeddings import AzureOpenAIEmbeddings, AzureOpenAIEmbeddingsOptions
from chromadb import EmbeddingFunction, Embeddings

from langchain_core.documents import Document
from langchain.text_splitter import CharacterTextSplitter, RecursiveCharacterTextSplitter

from .config import Config

config = Config()

# -----------Initializing Azure services clients----------------#
embeddings_client = AzureOpenAIEmbeddings(AzureOpenAIEmbeddingsOptions(
    azure_api_key=Config.AZURE_OPENAI_API_KEY,
    azure_endpoint=Config.AZURE_OPENAI_ENDPOINT,
    azure_deployment=Config.AZURE_OPENAI_EMBEDDING_DEPLOYMENT
))

#-------------------------Helper functions----------------------#
class ChromaEmbeddings(EmbeddingFunction):
    def __init__(self) -> None:
        pass
        # super().__init__()
    
    async def get_embeddings(self, docs: list[Document]) -> Embeddings:
        embeddings = []
        for doc in docs:
            result = await embeddings_client.create_embeddings(doc.page_content)
            if (result.status != 'success' or not result.output):
                raise Exception(f"Failed to generate embeddings for description: {doc.page_content}")
            embeddings.append(result.output[0])
        return embeddings

async def build_vector_store(documents: list[Document]):
    try:
        # Get the embedding function
        embedding_func = ChromaEmbeddings()
        # Split the PDF into smaller chunks
        text_splitter = CharacterTextSplitter(chunk_size=750, chunk_overlap=20)
        docs = text_splitter.split_documents(documents)        
        # Store the documents and embeddings in the client instance
        embeddings = await embedding_func.get_embeddings(docs)
        # Convert list[Document] into list[str]
        docs_str = [doc.page_content for doc in docs]
    except:
        raise Exception("Couldn't create embeddings for the uploaded file")
    return docs_str, embeddings

async def retrieval_file(query_text, collection):
    try:
        # Get the embedding function
        embedding_func = ChromaEmbeddings()
        # Generate embeddings of the query
        query_embedding = await embedding_func.get_embeddings([Document(page_content=query_text)])
        # Fetch the top-k results
        k = 3
        top_k_searchResults = collection.query(query_embedding, n_results=min(k, collection.count()))
        results_content = top_k_searchResults["documents"][0]
    except:
        raise Exception("Couldn't fetch results from the chromadb collection")
    # Return the documents as string
    docs = '\n`<context>\n'
    for i, text in enumerate(results_content):
        docs += f"Doc-{i+1}\n" + text + "\n\n"
    return docs + "\n</context>`\n"

    