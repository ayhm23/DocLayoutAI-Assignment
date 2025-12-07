from sentence_transformers import SentenceTransformer, util
import os

class RankingEngine:
    def __init__(self, model_name="intfloat/e5-small-v2", model_path=None):
        """
        Initializes the semantic ranking engine.
        If model_path is provided, it loads from there (Offline mode).
        Otherwise, it downloads from HuggingFace.
        """
        print(f"Initializing NLP Model: {model_name}...")
        
        if model_path and os.path.exists(model_path):
            print(f"Loading from local cache: {model_path}")
            self.model = SentenceTransformer(model_name, cache_folder=model_path)
        else:
            # Fallback for standard assignment usage
            print("Loading from HuggingFace (may require internet first run)...")
            self.model = SentenceTransformer(model_name)

    def rank_candidates(self, candidates, job_query, top_k=5):
        """
        Ranks heading candidates against the job_query using Cosine Similarity.
        (Renamed from match_candidates to match main.py)
        """
        if not candidates:
            return []

        candidate_texts = [c["text"] for c in candidates]
        
        # Vectorize
        embeddings = self.model.encode(candidate_texts, convert_to_tensor=True)
        query_embedding = self.model.encode(job_query, convert_to_tensor=True)

        # Compute Similarity
        cos_scores = util.cos_sim(query_embedding, embeddings)[0]
        
        # Get Top K
        k = min(top_k, len(candidate_texts))
        top_results = cos_scores.topk(k=k)

        matches = []
        for idx, score in zip(top_results.indices, top_results.values):
            c = candidates[idx]
            matches.append({
                "text": c["text"],
                "score": round(float(score), 3),
                "page_num": c["page_num"],
                "y": c["y"]
            })

        return matches