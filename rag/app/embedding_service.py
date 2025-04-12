from typing import List, Union
import torch
from transformers import AutoTokenizer, AutoModel
import numpy as np


class EmbeddingService:
    def __init__(self, model_name: str = "sentence-transformers/all-mpnet-base-v2"):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name).to(self.device)
        self.model.eval()

    def _mean_pooling(self, model_output, attention_mask):
        token_embeddings = model_output[0]
        input_mask_expanded = (
            attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
        )
        return torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(
            input_mask_expanded.sum(1), min=1e-9
        )

    @torch.no_grad()
    def get_embeddings(self, texts: Union[str, List[str]]) -> np.ndarray:
        """Generate embeddings for a single text or list of texts"""
        if isinstance(texts, str):
            texts = [texts]

        # Tokenize and prepare input
        encoded_input = self.tokenizer(
            texts, padding=True, truncation=True, max_length=512, return_tensors="pt"
        ).to(self.device)

        # Generate embeddings
        model_output = self.model(**encoded_input)
        embeddings = self._mean_pooling(model_output, encoded_input["attention_mask"])
        embeddings = torch.nn.functional.normalize(embeddings, p=2, dim=1)

        return embeddings.cpu().numpy()

    def get_query_embedding(self, query: str) -> np.ndarray:
        """Generate embedding for a single query"""
        return self.get_embeddings(query)[0]
