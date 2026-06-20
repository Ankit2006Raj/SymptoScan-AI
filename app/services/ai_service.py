import os
import re
import json
import pickle
import numpy as np
import faiss

# Set environment variables before importing torch/transformers
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
os.environ["PYTORCH_MPS_HIGH_WATERMARK_RATIO"] = "0.0"
os.environ["TOKENIZERS_PARALLELISM"] = "false"
os.environ["OMP_NUM_THREADS"] = "1"

from sentence_transformers import SentenceTransformer
import torch
import logging

logger = logging.getLogger(__name__)

# Load these globally to avoid reloading on every request
from app.services.sapbert_service import sapbert_service
try:
    DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
    FAISS_INDEX_PATH = os.path.join(DATA_DIR, 'faiss.index')
    METADATA_PATH = os.path.join(DATA_DIR, 'metadata.pkl')
    
    if os.path.exists(FAISS_INDEX_PATH) and os.path.exists(METADATA_PATH):
        faiss_index = faiss.read_index(FAISS_INDEX_PATH)
        with open(METADATA_PATH, 'rb') as f:
            metadata = pickle.load(f)
            
        # Using standard sentence-transformers model on CPU to prevent Mac MPS segfaults
        embedder = SentenceTransformer('all-MiniLM-L6-v2', device='cpu')
    else:
        faiss_index = None
        metadata = None
        embedder = None
except Exception as e:
    logger.error(f"Error loading RAG models: {e}")
    faiss_index = None
    metadata = None
    embedder = None

from app.services.rule_engine import MedicalRuleEngine

class AIService:
    def __init__(self):
        self.rule_engine = MedicalRuleEngine()
        
    def _normalize_symptoms(self, text):
        text = text.lower()
        text = re.sub(r'[^\w\s]', ' ', text)
        return text.strip()

    def get_rag_matches(self, query, normalized_symptoms_text, user_symptoms_raw, severity, rule_output, top_k=5):
        logger.info(f"Retrieving RAG matches for query top_k={top_k}")
        if not faiss_index or not embedder or not metadata:
            logger.warning("RAG context unavailable: dependencies or models missing.")
            return []
            
        try:
            query_embedding = embedder.encode([query])
            distances, indices = faiss_index.search(query_embedding.astype(np.float32), top_k)
            
            matches = []
            for i, idx in enumerate(indices[0]):
                if idx < len(metadata) and idx >= 0:
                    item = metadata[idx]
                    dist = distances[0][i]
                    # Lower distance = higher confidence in FAISS L2
                    faiss_sim = max(0.0, 100.0 - (dist * 12.0))
                    
                    # SapBERT Similarity with disease name
                    disease_name = item.get('disease', 'Unknown')
                    sapbert_sim = sapbert_service.get_similarity_score(user_symptoms_raw, disease_name) * 100
                    
                    # Symptom overlap scoring
                    item_symptoms = [s.lower().replace('_', ' ') for s in item.get('symptoms', [])]
                    user_symptoms_list = [s.strip() for s in normalized_symptoms_text.split(',')]
                    overlap = set(item_symptoms).intersection(set(user_symptoms_list))
                    overlap_score = min(100.0, (len(overlap) / max(1, len(user_symptoms_list))) * 100)
                    
                    # Disease severity weighting
                    severity_weight = min(100.0, severity * 10)
                    
                    # Combine multi-factor scoring
                    final_score = (faiss_sim * 0.4) + (sapbert_sim * 0.3) + (overlap_score * 0.2) + (severity_weight * 0.1)
                    
                    # Boost if rule engine flagged an emergency
                    if rule_output.get('has_emergency'):
                        final_score += 15
                    
                    matches.append({
                        "name": disease_name,
                        "confidence_score": min(99, int(final_score)),
                        "description": item.get('description', ''),
                        "precautions": item.get('precautions', [])
                    })
            
            logger.info(f"RAG Retrieval successful. Found {len(matches)} matches.")
            # Sort by confidence
            matches = sorted(matches, key=lambda x: x['confidence_score'], reverse=True)
            return matches
        except Exception as e:
            logger.exception(f"RAG search error: {e}")
            return []

    def analyze_symptoms(self, data):
        """
        data: dict containing age, gender, symptoms, duration, severity, medical_history
        """
        logger.info("Starting local symptom analysis pipeline with SapBERT")
        
        symptoms = data.get('symptoms', '')
        normalized_symptoms = self._normalize_symptoms(symptoms)
        
        # 1. SapBERT Processing
        canonical_symptoms = sapbert_service.normalize_symptoms(normalized_symptoms)
        
        severity = int(data.get('severity', 0)) if str(data.get('severity')).isdigit() else 0
        
        logger.info("Evaluating Medical Rule Engine")
        rule_output = self.rule_engine.evaluate(data)
        logger.info(f"Rule Engine Output: {rule_output}")
        
        user_profile = f"Patient Profile: Age {data.get('age')}, Gender {data.get('gender')}. " \
                       f"Medical History: {data.get('medical_history', 'None reported')}. " \
                       f"Symptoms: {canonical_symptoms}. " \
                       f"Duration: {data.get('duration')}. " \
                       f"Severity: {severity}/10."

        matches = self.get_rag_matches(user_profile, canonical_symptoms, symptoms, severity, rule_output, top_k=3)
        
        conditions = []
        for m in matches:
            conditions.append({
                "name": m['name'].strip(),
                "confidence_score": m['confidence_score']
            })
            
        if not conditions:
            conditions = [{"name": "Undetermined Condition", "confidence_score": 50}]
            
        risk_level = "Low"
        highest_conf = conditions[0]['confidence_score'] if conditions else 0
        
        if highest_conf > 85 or severity > 6:
            risk_level = "Moderate"
            
        if rule_output.get('risk_override'):
            risk_level = rule_output['risk_override']
            
        cond_names = [c['name'] for c in conditions]
        explanation = f"Based on semantic similarity of your symptoms with our medical database, possible conditions include {', '.join(cond_names)}."
        if matches and matches[0]['description']:
            explanation += f" {matches[0]['name']} is described as: {matches[0]['description']}"
            
        if rule_output.get('has_emergency'):
            explanation += " CRITICAL: Emergency symptoms were detected that require immediate attention."
            
        recommendations = []
        if matches and matches[0].get('precautions'):
            recommendations.extend([p.strip() for p in matches[0]['precautions'] if p.strip()])
        else:
            recommendations.extend(["Rest and monitor symptoms.", "Stay hydrated."])
            
        if rule_output.get('recommendations'):
            recommendations = rule_output['recommendations'] + recommendations
            
        red_flag_warnings = rule_output.get('warnings', [])
        
        follow_up_questions = [
            f"Are you experiencing any other symptoms related to {cond_names[0]}?",
            "Have your symptoms progressively worsened over the last 24 hours?"
        ]
        
        parsed_result = {
            "conditions": conditions,
            "risk_level": risk_level,
            "explanation": explanation,
            "recommendations": list(dict.fromkeys(recommendations)),
            "red_flag_warnings": list(set(red_flag_warnings)),
            "follow_up_questions": follow_up_questions
        }
        
        logger.info("Local processing complete. Returning final JSON.")
        return parsed_result
