import numpy as np
from scripts.ai import LLMCaller

llmcaller = LLMCaller()

def vectorize(chunks: list[dict[str, str]]) -> list[list[float]]:
    """
    Vectorizes the chunks using gemini-embedding-module

    :param chunks: List of the atomized text, each chunk will be vectorized
    :return: Returns the vectors to store in db
    """

    list_of_chunks = [chunk['text'] for chunk in chunks]
    response = llmcaller.get_embeddings(list_of_chunks)

    return [emb.values for emb in response] 

def normalize_embeding(old_embeding_values: list[float]) -> np.ndarray:
    # might wanna check for 0 division later
    np_values = np.array(old_embeding_values, dtype=np.float64)
    return np_values / np.linalg.norm(np_values)
    