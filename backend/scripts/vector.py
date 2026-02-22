from scripts.ai import LLMCaller

llmcaller = LLMCaller()

def vectorize(chunks: dict[str, list[dict[str, str]]]) -> list[list[float]]:
    """
    Vectorizes the chunks using gemini-embedding-module

    :param chunks: List of the atomized text, each chunk will be vectorized
    :return: Returns the vectors to store in db
    """
    print("HAHA", chunks)
    list_of_chunks = [chunk['text'] for chunk in chunks['chunks']]
    response = llmcaller.get_embeddings(list_of_chunks)

    return [emb.values for emb in response] 

