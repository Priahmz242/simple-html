"""
Memory System
=============

Manages the AI agent's memory, knowledge graph, and experience storage.
"""

import json
import hashlib
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Any
import numpy as np

class KnowledgeGraph:
    """Knowledge Graph for storing concepts and relationships"""
    
    def __init__(self, storage_path: str = 'knowledge/knowledge_graph.json'):
        self.storage_path = Path(storage_path)
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        self.graph = self._load()
    
    def _load(self) -> Dict:
        if self.storage_path.exists():
            with open(self.storage_path, 'r') as f:
                return json.load(f)
        return {'nodes': [], 'edges': [], 'concepts': {}}
    
    def _save(self) -> None:
        with open(self.storage_path, 'w') as f:
            json.dump(self.graph, f, indent=2)
    
    def add_concept(self, name: str, category: str, description: str, source: Optional[str] = None) -> bool:
        if name in self.graph['concepts']:
            return False
        
        self.graph['concepts'][name] = {
            'category': category,
            'description': description,
            'source': source,
            'added': datetime.now().isoformat(),
            'connections': []
        }
        self.graph['nodes'].append(name)
        self._save()
        return True
    
    def add_relation(self, concept1: str, concept2: str, relation_type: str) -> bool:
        if concept1 not in self.graph['concepts'] or concept2 not in self.graph['concepts']:
            return False
        
        self.graph['edges'].append({
            'source': concept1,
            'target': concept2,
            'type': relation_type
        })
        self.graph['concepts'][concept1]['connections'].append({
            'to': concept2,
            'type': relation_type
        })
        self._save()
        return True
    
    def get_related(self, concept: str, max_distance: int = 2) -> List[str]:
        related = set()
        if concept not in self.graph['concepts']:
            return []
        
        for conn in self.graph['concepts'][concept]['connections']:
            related.add(conn['to'])
            if max_distance >= 2:
                for sub_conn in self.graph['concepts'].get(conn['to'], {}).get('connections', []):
                    related.add(sub_conn['to'])
        
        return list(related)
    
    def get_summary(self) -> Dict:
        return {
            'total_concepts': len(self.graph['concepts']),
            'total_edges': len(self.graph['edges']),
            'categories': list(set(c['category'] for c in self.graph['concepts'].values()))
        }


class NeuralMemory:
    """Neural Memory for vector-based storage"""
    
    def __init__(self, storage_path: str = 'knowledge/memory.db'):
        self.storage_path = Path(storage_path)
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        self.memory = {'experiences': [], 'knowledge': [], 'patterns': [], 'embeddings': {}}
        self._load()
    
    def _load(self):
        memory_file = self.storage_path / 'memory.json'
        if memory_file.exists():
            with open(memory_file, 'r') as f:
                self.memory = json.load(f)
    
    def _save(self):
        with open(self.storage_path / 'memory.json', 'w') as f:
            json.dump(self.memory, f, indent=2)
    
    def _get_embedding(self, text: str) -> List[float]:
        hash_obj = hashlib.sha256(text.encode())
        hash_bytes = hash_obj.digest()
        embedding = np.frombuffer(hash_bytes[:64], dtype=np.uint8).astype(np.float32)
        embedding = embedding / 255.0 * 2 - 1
        return embedding.tolist()
    
    def store_experience(self, experience: str, metadata: Optional[Dict] = None) -> str:
        doc_id = f"exp_{datetime.now().timestamp()}"
        embedding = self._get_embedding(experience)
        
        entry = {
            'id': doc_id,
            'text': experience,
            'embedding': embedding,
            'metadata': metadata or {},
            'timestamp': datetime.now().isoformat()
        }
        self.memory['experiences'].append(entry)
        self.memory['embeddings'][doc_id] = embedding
        self._save()
        return doc_id
    
    def store_knowledge(self, text: str, category: str, source: Optional[str] = None) -> str:
        doc_id = f"know_{datetime.now().timestamp()}"
        embedding = self._get_embedding(text)
        
        entry = {
            'id': doc_id,
            'text': text,
            'embedding': embedding,
            'category': category,
            'source': source,
            'timestamp': datetime.now().isoformat()
        }
        self.memory['knowledge'].append(entry)
        self.memory['embeddings'][doc_id] = embedding
        self._save()
        return doc_id
    
    def recall_similar(self, query: str, top_n: int = 5, collection: str = 'knowledge') -> List[Dict]:
        query_embedding = self._get_embedding(query)
        items = self.memory.get(collection, [])
        
        scored_items = []
        for item in items:
            item_embedding = item.get('embedding', [])
            if item_embedding:
                similarity = np.dot(query_embedding, item_embedding) / (
                    np.linalg.norm(query_embedding) * np.linalg.norm(item_embedding) + 1e-8
                )
                scored_items.append((similarity, item))
        
        scored_items.sort(key=lambda x: x[0], reverse=True)
        return [item for _, item in scored_items[:top_n]]
    
    def get_summary(self) -> Dict:
        return {
            'total_experiences': len(self.memory['experiences']),
            'total_knowledge': len(self.memory['knowledge']),
            'total_patterns': len(self.memory['patterns'])
        }


class Memory:
    """Core Memory - Orchestrates all memory systems"""
    
    def __init__(self):
        self.knowledge_graph = KnowledgeGraph()
        self.neural_memory = NeuralMemory()
    
    def learn_from_text(self, text: str, category: str, source: Optional[str] = None) -> bool:
        self.neural_memory.store_knowledge(text, category, source)
        return True
    
    def remember(self, query: str, top_n: int = 5) -> List[Dict]:
        return self.neural_memory.recall_similar(query, top_n)
    
    def get_summary(self) -> Dict:
        return {
            'knowledge_graph': self.knowledge_graph.get_summary(),
            'neural_memory': self.neural_memory.get_summary()
        }
