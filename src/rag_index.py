# ---------------Importing libraries----------------------------#
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.models import VectorizedQuery
from teams.ai.embeddings import AzureOpenAIEmbeddings, AzureOpenAIEmbeddingsOptions
from .config import Config

from .classify_query import extract_features, classify_text

config = Config()

# -----------Initializing Azure services clients----------------#
search_client = SearchClient(endpoint=config.AZURE_SEARCH_ENDPOINT, 
                             index_name=config.INDEX_NAME, 
                             credential=AzureKeyCredential(config.AZURE_SEARCH_KEY),
                            )
embeddings = AzureOpenAIEmbeddings(AzureOpenAIEmbeddingsOptions(
    azure_api_key=Config.AZURE_OPENAI_API_KEY,
    azure_endpoint=Config.AZURE_OPENAI_ENDPOINT,
    azure_deployment=Config.AZURE_OPENAI_EMBEDDING_DEPLOYMENT
))

#-------------------------Helper functions----------------------#
async def get_embedding_vector(text: str):
    
    result = await embeddings.create_embeddings(text)
    if (result.status != 'success' or not result.output):
        raise Exception(f"Failed to generate embeddings for description: {text}")
    
    return result.output[0]

async def retrieval(query: str, vector_query, category: str):
    # Hybrid search without reranking
    if category=='simple':
        results_vec = search_client.search(search_text=None,  
                                           vector_queries=[vector_query],
                                           select=["title", "chunk"],
                                           search_fields=['chunk']
                                          )
        return results_vec
    elif category=='intermediate':
        results_hyb = search_client.search(search_text=query,  
                                           vector_queries=[vector_query],
                                           select=["title", "chunk"], 
                                           top=10, # For keyword search
                                           search_fields=['chunk']
                                          )
        return results_hyb
    elif category=='complex':
        # Run a hybrid query with semantic reranking
        results_hyb_rerank = search_client.search(search_text=query,  
                                                  vector_queries=[vector_query],
                                                  select=["title", "chunk"], 
                                                  top=10,
                                                  search_fields=['chunk'],
                                                  query_type='semantic', 
                                                  semantic_configuration_name='test-semantic-config',
                                                  query_caption='extractive'
                                                )
        return results_hyb_rerank

#-------------------------Main RAG function-----------------------#
async def retrieval_index(query: str):
    # Edge case
    if not query:
        return ""
    # Extract the query's features and classify it
    try:
        features = extract_features(query)
        category = classify_text(features)
    except:
        raise Exception("Couldn't extract features or classify the given query.")
    # Get the embeddings
    embedding = await get_embedding_vector(query)
    # Get a vector query from the embeddings
    vector_query = VectorizedQuery(vector=embedding, 
                                   k_nearest_neighbors=10, 
                                   fields="text_vector", 
                                   exhaustive=False
                                  )
    # Perform retrieval from our index
    searchResults = await retrieval(query, vector_query, category)
    if not searchResults:
        raise Exception("Couldn't retrieve docs from the index.")
    # Fetch the top k results
    k = 3
    top_k_searchResults = [search_result for i, search_result in enumerate(searchResults) if i<k]
    docs = '\n`<context>\n'
    for i, result in enumerate(top_k_searchResults):
        docs += f"Doc-{i+1}\n" + result["chunk"] + "\n\n"
    return docs + "\n</context>`\n"