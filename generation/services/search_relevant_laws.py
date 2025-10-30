import pandas as pd
import numpy as np
from timeit import default_timer as timer
from sentence_transformers import SentenceTransformer
# Load precomputed embeddings and text chunks
text_chunks_and_embedding_df = pd.read_csv("../data/text_chunks_and_embeddings_df.csv")
print(f"Loaded {len(text_chunks_and_embedding_df)} text chunks and embeddings.")

# Convert embedding column back to np.array (expects format like "[0.1 0.2 ...]")
text_chunks_and_embedding_df["embedding"] = text_chunks_and_embedding_df["embedding"].apply(
    lambda x: np.fromstring(x.strip("[]"), sep=" ")
)

# Convert texts and embedding df to list of dicts for later lookup
pages_and_chunks = text_chunks_and_embedding_df.to_dict(orient="records")

# Build numpy matrix of embeddings for fast dot-product/cosine computations
_emb_list = text_chunks_and_embedding_df["embedding"].tolist()
if len(_emb_list) == 0:
    embeddings_matrix = np.zeros((0, 0), dtype=np.float32)
else:
    embeddings_matrix = np.vstack(_emb_list).astype(np.float32)


def _compute_cosine_scores(query_emb: np.ndarray, emb_matrix: np.ndarray) -> np.ndarray:
    # normalize and compute cosine similarity
    if emb_matrix.size == 0:
        return np.array([])
    q = query_emb.astype(np.float32)
    # normalize
    q_norm = q / np.linalg.norm(q) if np.linalg.norm(q) != 0 else q
    m_norm = emb_matrix / np.linalg.norm(emb_matrix, axis=1, keepdims=True)
    # dot product
    scores = m_norm.dot(q_norm)
    return scores


def retrieve_relevant_laws(
    query: str,
    n_resources_to_return: int = 5,
    print_time: bool = True
):
    """
    Embeds a query (requires `sentence-transformers` to be installed) and returns
    the top-k most relevant law chunks from precomputed embeddings.

    If `sentence_transformers` is not available, this function raises a clear
    error explaining how to enable semantic search.
    """

    # Load a small/appropriate model (this will download if not cached)
    model = SentenceTransformer("huyydangg/DEk21_hcmute_embedding")

    # Embed the query
    start_time = timer()
    query_embedding = model.encode(query)
    end_time = timer()

    if print_time:
        print(f"[INFO] Time taken to embed query: {end_time - start_time:.5f} seconds.")

    # Compute similarity scores (cosine)
    scores = _compute_cosine_scores(query_embedding, embeddings_matrix)

    if scores.size == 0:
        return []

    # Get top k indices
    topk_idx = np.argsort(-scores)[:n_resources_to_return]

    data = []
    for idx in topk_idx:
        data.append({
            "score": float(scores[idx]),
            "sentence_chunk": pages_and_chunks[int(idx)]["sentence_chunk"],
            "page_number": pages_and_chunks[int(idx)]["page_number"]
        })

    return data