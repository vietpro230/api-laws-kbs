import pandas as pd
import numpy as np
import torch
from timeit import default_timer as timer
from sentence_transformers import SentenceTransformer, util

# Load embedding model
embedding_model = SentenceTransformer("huyydangg/DEk21_hcmute_embedding")

# Import texts and embedding df
text_chunks_and_embedding_df = pd.read_csv("../data/text_chunks_and_embeddings_df.csv")
print(f"Loaded {len(text_chunks_and_embedding_df)} text chunks and embeddings.")

# Convert embedding column back to np.array
text_chunks_and_embedding_df["embedding"] = text_chunks_and_embedding_df["embedding"].apply(
    lambda x: np.fromstring(x.strip("[]"), sep=" ")
)

# Convert texts and embedding df to list of dicts
pages_and_chunks = text_chunks_and_embedding_df.to_dict(orient="records")

# Convert embeddings to torch tensor and send to device
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
embeddings = torch.tensor(
    np.array(text_chunks_and_embedding_df["embedding"].tolist()),
    dtype=torch.float32
).to(device)
embeddings.shape

def retrieve_relevant_laws(
    query: str,
    n_resources_to_return: int = 5,
    print_time: bool = True
):
    """
    Embeds a query with model and returns top k scores and indices from embeddings.
    """
    # Embed the query
    query_embedding = embedding_model.encode(query, convert_to_tensor=True)

    # Get dot product scores on embeddings
    start_time = timer()
    dot_scores = util.dot_score(query_embedding, embeddings)[0]
    end_time = timer()

    if print_time:
        print(f"[INFO] Time taken to get scores on {len(embeddings)} embeddings: {end_time - start_time:.5f} seconds.")

    scores, indices = torch.topk(dot_scores, k=n_resources_to_return)
    data = []

    for score, index in zip(scores, indices):
        data.append({
            "score": score.item(),
            "sentence_chunk": pages_and_chunks[index]["sentence_chunk"],
            "page_number": pages_and_chunks[index]["page_number"]
        })

    return data