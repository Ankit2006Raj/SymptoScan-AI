import os
import json
import logging
import torch
from transformers import AutoTokenizer, AutoModel

logger = logging.getLogger(__name__)

class SapBERTService:
    def __init__(self):
        self.model_name = "cambridgeltl/SapBERT-from-PubMedBERT-fulltext"
        self.tokenizer = None
        self.model = None
        self.canonical_symptoms = []
        self.symptom_embeddings = None
        
        self._load_model()
        self._load_canonical_symptoms()

    def _load_model(self):
        try:
            logger.info("Loading SapBERT model for medical terminology...")
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModel.from_pretrained(self.model_name).to('cpu')
            self.model.eval()
            logger.info("SapBERT model loaded successfully.")
        except Exception as e:
            logger.error(f"Failed to load SapBERT model: {e}")

    def _load_canonical_symptoms(self):
        try:
            data_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'medical_knowledge.json')
            if not os.path.exists(data_path):
                logger.warning("medical_knowledge.json not found.")
                return

            with open(data_path, 'r') as f:
                knowledge = json.load(f)

            symptoms_set = set()
            for entry in knowledge:
                for sym in entry.get('symptoms', []):
                    # Replace underscores and clean up
                    clean_sym = sym.replace('_', ' ').strip().lower()
                    if clean_sym:
                        symptoms_set.add(clean_sym)
            
            self.canonical_symptoms = list(symptoms_set)
            
            # Pre-compute embeddings for canonical symptoms
            if self.model and self.canonical_symptoms:
                logger.info(f"Computing SapBERT embeddings for {len(self.canonical_symptoms)} canonical symptoms...")
                self.symptom_embeddings = self._get_embeddings(self.canonical_symptoms)
                logger.info("Canonical symptom embeddings computed.")
        except Exception as e:
            logger.error(f"Failed to load canonical symptoms: {e}")

    def _get_embeddings(self, texts):
        if not self.model or not self.tokenizer or not texts:
            return None
            
        try:
            inputs = self.tokenizer(texts, padding=True, truncation=True, return_tensors="pt", max_length=128)
            inputs = {k: v.to('cpu') for k, v in inputs.items()}
            with torch.no_grad():
                outputs = self.model(**inputs)
                # Use CLS token embedding
                cls_embeddings = outputs.last_hidden_state[:, 0, :]
                # Normalize for cosine similarity
                cls_embeddings = torch.nn.functional.normalize(cls_embeddings, p=2, dim=1)
                return cls_embeddings
        except Exception as e:
            logger.error(f"Error computing SapBERT embeddings: {e}")
            return None

    def normalize_symptoms(self, user_text):
        """
        Takes raw user text, identifies potential symptoms and maps them to canonical terms.
        """
        if not self.model or self.symptom_embeddings is None:
            return user_text

        # Basic chunking: split by comma or 'and' to isolate symptom phrases
        import re
        parts = re.split(r',|\sand\s|\sor\s|\n', user_text)
        parts = [p.strip().lower() for p in parts if p.strip()]

        normalized_terms = []
        for part in parts:
            if not part:
                continue
            
            part_emb = self._get_embeddings([part])
            if part_emb is None:
                normalized_terms.append(part)
                continue
                
            # Compute cosine similarity
            similarity = torch.mm(part_emb, self.symptom_embeddings.transpose(0, 1)).squeeze(0)
            best_idx = torch.argmax(similarity).item()
            best_score = similarity[best_idx].item()
            
            # Threshold for accepting a canonical mapping
            if best_score > 0.65:
                matched_sym = self.canonical_symptoms[best_idx]
                logger.info(f"SapBERT mapped '{part}' -> '{matched_sym}' (score: {best_score:.2f})")
                normalized_terms.append(matched_sym)
            else:
                normalized_terms.append(part)
                
        return ", ".join(normalized_terms)
        
    def get_similarity_score(self, text1, text2):
        """
        Computes the SapBERT similarity score between two texts.
        """
        if not self.model:
            return 0.0
            
        emb1 = self._get_embeddings([text1])
        emb2 = self._get_embeddings([text2])
        if emb1 is None or emb2 is None:
            return 0.0
            
        similarity = torch.mm(emb1, emb2.transpose(0, 1)).item()
        return max(0.0, similarity)

# Instantiate a singleton to avoid reloading on every request
sapbert_service = SapBERTService()
