import logging
from pathlib import Path
import pandas as pd
import numpy as np
from timeit import default_timer as timer

# Module logger
logger = logging.getLogger("generation.search_relevant_laws")
if not logger.handlers:
    # defer to parent handlers (configured by generation_pipeline) if present
    handler = logging.NullHandler()
    logger.addHandler(handler)

# Resolve data path relative to this file so it works in Docker / different CWDs
DATA_CSV = Path(__file__).resolve().parents[2] / "data" / "text_chunks_and_embeddings_df.csv"
if not DATA_CSV.exists():
    logger.error("Embeddings CSV not found at %s", DATA_CSV)
    raise FileNotFoundError(f"Embeddings CSV not found at {DATA_CSV}")

try:
    text_chunks_and_embedding_df = pd.read_csv(str(DATA_CSV))
    logger.info("Loaded %d text chunks and embeddings from %s.", len(text_chunks_and_embedding_df), DATA_CSV)
except Exception:
    logger.exception("Failed to load text_chunks_and_embeddings_df.csv from %s", DATA_CSV)
    raise

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
    logger.warning("Embeddings dataframe contained zero rows")
else:
    try:
        embeddings_matrix = np.vstack(_emb_list).astype(np.float32)
    except Exception:
        logger.exception("Failed to build embeddings matrix from stored embeddings")
        raise

# Cache sentence-transformers model after first load to avoid repeated downloads
_SENTENCE_MODEL = None


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

    # Load sentence-transformers lazily to avoid module import errors at import time
    global _SENTENCE_MODEL
    try:
        from sentence_transformers import SentenceTransformer  # local import
    except Exception:
        logger.exception("sentence-transformers is not available; cannot embed query")
        raise ModuleNotFoundError(
            "sentence-transformers is required to embed queries. Install it (and torch) or use an external embedding service."
        )

    # Load model once
    try:
        if _SENTENCE_MODEL is None:
            logger.info("Loading SentenceTransformer model for the first time")
            _SENTENCE_MODEL = SentenceTransformer("huyydangg/DEk21_hcmute_embedding")
        model = _SENTENCE_MODEL
    except Exception:
        logger.exception("Failed to load SentenceTransformer model")
        raise

    # Embed the query
    try:
        start_time = timer()
        query_embedding = model.encode(query)
        end_time = timer()
        if print_time:
            logger.info("Time taken to embed query: %.5f seconds.", end_time - start_time)
    except Exception:
        logger.exception("Failed while encoding query")
        raise

    # Compute similarity scores (cosine)
    scores = _compute_cosine_scores(query_embedding, embeddings_matrix)

    if scores.size == 0:
        logger.info("No embeddings available to score; returning empty list")
        return []

    # Get top k indices
    topk_idx = np.argsort(-scores)[:n_resources_to_return]

    data = []
    for idx in topk_idx:
        try:
            data.append({
                "score": float(scores[idx]),
                "sentence_chunk": pages_and_chunks[int(idx)]["sentence_chunk"],
                "page_number": pages_and_chunks[int(idx)]["page_number"]
            })
        except Exception:
            logger.exception("Failed to build data entry for index %s", idx)

    logger.info("Returning %d relevant documents for query.", len(data))
    return data