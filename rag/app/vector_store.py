import faiss
import numpy as np
from typing import List, Dict
import pickle
from pathlib import Path


class VectorStore:
    def __init__(self, dimension: int = 768):
        self.dimension = dimension
        self.index = faiss.IndexFlatL2(dimension)
        self.document_map: Dict[int, Dict] = {}
        self.current_id = 0

    def add_embeddings(self, embeddings: List[np.ndarray], metadata: List[Dict]):
        if len(embeddings) != len(metadata):
            raise ValueError(
                "Number of embeddings must match number of metadata entries"
            )

        embeddings_array = np.array(embeddings).astype("float32")
        ids = np.array([self.current_id + i for i in range(len(embeddings))])

        self.index.add(embeddings_array)

        for i, meta in enumerate(metadata):
            self.document_map[int(ids[i])] = meta

        self.current_id += len(embeddings)

    def search(self, query_embedding: np.ndarray, k: int = 5) -> List[Dict]:
        query_embedding = query_embedding.astype("float32").reshape(1, -1)
        distances, indices = self.index.search(query_embedding, k)

        results = []
        for i, idx in enumerate(indices[0]):
            if idx != -1:  # Valid index
                result = self.document_map[int(idx)].copy()
                result["distance"] = float(distances[0][i])
                results.append(result)

        return results

    def save(self, path: str):
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)

        # Save the FAISS index
        faiss.write_index(self.index, str(path) + ".index")

        # Save the document map
        with open(str(path) + ".pkl", "wb") as f:
            pickle.dump(
                {
                    "document_map": self.document_map,
                    "current_id": self.current_id,
                    "dimension": self.dimension,
                },
                f,
            )

    @classmethod
    def load(cls, path: str):
        path = Path(path)

        # Load the FAISS index
        index = faiss.read_index(str(path) + ".index")

        # Load the document map and metadata
        with open(str(path) + ".pkl", "rb") as f:
            data = pickle.load(f)

        instance = cls(dimension=data["dimension"])
        instance.index = index
        instance.document_map = data["document_map"]
        instance.current_id = data["current_id"]

        return instance
