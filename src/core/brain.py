"""
Brain Module
============

The core intelligence engine for the Boijelux AI Agent.
"""

import json
import hashlib
import numpy as np
from datetime import datetime
from typing import Dict, Any, Optional, List

from .memory import Memory

class TaskEmbedding:
    """Convert tasks to numerical representations"""
    
    def __init__(self, embedding_dim: int = 256):
        self.embedding_dim = embedding_dim
    
    def encode(self, text: str) -> np.ndarray:
        hash_obj = hashlib.sha256(text.encode())
        hash_bytes = hash_obj.digest()
        embedding = np.frombuffer(hash_bytes[:self.embedding_dim], dtype=np.uint8).astype(np.float32)
        embedding = embedding / 255.0 * 2 - 1
        return embedding


class Brain:
    """Universal Brain - Handles ANY task, ANY domain"""
    
    def __init__(self, memory: Memory):
        self.memory = memory
        self.embedder = TaskEmbedding()
        self.domains = self._initialize_domains()
        self.current_domain = None
        self.task_history = []
    
    def _initialize_domains(self) -> Dict:
        """Initialize all domain handlers"""
        from ..domains import (
            BusinessDomain, FinanceDomain, HealthcareDomain,
            EducationDomain, TechnologyDomain, LegalDomain,
            CreativeDomain, RealEstateDomain, ManufacturingDomain,
            AgricultureDomain, RetailDomain, TransportationDomain,
            EnergyDomain, GovernmentDomain
        )
        
        return {
            'business': BusinessDomain(),
            'finance': FinanceDomain(),
            'healthcare': HealthcareDomain(),
            'education': EducationDomain(),
            'technology': TechnologyDomain(),
            'legal': LegalDomain(),
            'creative': CreativeDomain(),
            'real_estate': RealEstateDomain(),
            'manufacturing': ManufacturingDomain(),
            'agriculture': AgricultureDomain(),
            'retail': RetailDomain(),
            'transportation': TransportationDomain(),
            'energy': EnergyDomain(),
            'government': GovernmentDomain()
        }
    
    def understand_task(self, task_description: str, context: Optional[Dict] = None) -> Dict:
        """Understand a task and create a plan"""
        domain = self._identify_domain(task_description)
        self.current_domain = domain
        
        task_vector = self.embedder.encode(task_description)
        context_vector = self.embedder.encode(json.dumps(context or {}))
        
        domain_knowledge = self.domains[domain].get_knowledge(task_description)
        similar_tasks = self.memory.remember(task_description)
        plan = self._create_plan(task_description)
        
        return {
            'domain': domain,
            'task_vector': task_vector.tolist(),
            'knowledge': domain_knowledge,
            'similar_tasks': similar_tasks,
            'plan': plan,
            'task_description': task_description
        }
    
    def _identify_domain(self, task_description: str) -> str:
        """Identify the domain of a task"""
        domain_keywords = {
            'business': ['business', 'management', 'company', 'strategy', 'ceo', 'manager'],
            'finance': ['finance', 'trade', 'investment', 'stock', 'market', 'price', 'crypto'],
            'healthcare': ['health', 'doctor', 'patient', 'medical', 'hospital', 'disease'],
            'education': ['education', 'school', 'study', 'teach', 'learn', 'student'],
            'technology': ['technology', 'software', 'hardware', 'network', 'computer', 'system'],
            'legal': ['legal', 'law', 'court', 'attorney', 'contract', 'rights'],
            'creative': ['creative', 'design', 'art', 'music', 'writing', 'media'],
            'real_estate': ['estate', 'property', 'land', 'house', 'rent'],
            'manufacturing': ['manufacturing', 'factory', 'production', 'warehouse', 'logistics'],
            'agriculture': ['agriculture', 'farming', 'crop', 'livestock', 'farm'],
            'retail': ['retail', 'store', 'shop', 'sales', 'customer'],
            'transportation': ['transportation', 'delivery', 'shipping', 'logistics', 'vehicle'],
            'energy': ['energy', 'power', 'electricity', 'solar', 'wind'],
            'government': ['government', 'policy', 'regulation', 'public', 'administration']
        }
        
        best_domain = 'general'
        best_score = 0
        
        for domain, keywords in domain_keywords.items():
            score = sum(1 for kw in keywords if kw.lower() in task_description.lower())
            if score > best_score:
                best_score = score
                best_domain = domain
        
        return best_domain
    
    def _create_plan(self, task: str) -> Dict:
        """Create an execution plan"""
        return {
            'steps': self._generate_steps(task),
            'tools': self._identify_tools(task),
            'subtasks': self._split_into_subtasks(task),
            'estimated_duration': self._estimate_duration(task)
        }
    
    def _generate_steps(self, task: str) -> List[str]:
        steps = [
            "1. Analyze task requirements",
            "2. Gather necessary information",
            "3. Process and analyze data",
            "4. Execute core action",
            "5. Verify results",
            "6. Learn from outcome"
        ]
        
        if 'trading' in task.lower() or 'investment' in task.lower():
            steps.insert(3, "3a. Perform technical analysis")
            steps.insert(4, "3b. Execute trade with risk management")
        
        if 'business' in task.lower():
            steps.insert(3, "3a. Perform market research")
            steps.insert(4, "3b. Generate business strategy")
        
        return steps
    
    def _identify_tools(self, task: str) -> List[str]:
        tools = []
        if any(kw in task.lower() for kw in ['analyze', 'data', 'statistics']):
            tools.append('Data Analysis')
        if any(kw in task.lower() for kw in ['trading', 'market', 'investment']):
            tools.append('Market Analysis')
        if any(kw in task.lower() for kw in ['write', 'create', 'content']):
            tools.append('Content Generation')
        if any(kw in task.lower() for kw in ['code', 'develop', 'program']):
            tools.append('Code Generation')
        return tools
    
    def _split_into_subtasks(self, task: str) -> List[str]:
        words = task.split()
        if len(words) > 15:
            return [' '.join(words[i:i+10]) for i in range(0, len(words), 10)]
        return [task]
    
    def _estimate_duration(self, task: str) -> str:
        word_count = len(task.split())
        if word_count < 10:
            return "5 minutes"
        elif word_count < 30:
            return "30 minutes"
        elif word_count < 50:
            return "2 hours"
        else:
            return "4+ hours"
    
    def execute(self, task_understanding: Dict) -> Dict:
        """Execute the understood task"""
        domain = task_understanding['domain']
        plan = task_understanding['plan']
        
        domain_handler = self.domains[domain]
        results = []
        
        for step in plan['steps']:
            try:
                result = domain_handler.execute_step(step, task_understanding)
                results.append({'step': step, 'status': 'success', 'result': result})
            except Exception as e:
                results.append({'step': step, 'status': 'failed', 'error': str(e)})
        
        final_result = domain_handler.generate_report(results, task_understanding)
        
        return {
            'success': all(r['status'] == 'success' for r in results),
            'results': results,
            'final_result': final_result,
            'domain': domain,
            'plan': plan
        }
    
    def process_task(self, task_description: str, context: Optional[Dict] = None) -> Dict:
        """Complete task processing pipeline"""
        understanding = self.understand_task(task_description, context)
        result = self.execute(understanding)
        return result
    
    def get_status(self) -> Dict:
        return {
            'domains': list(self.domains.keys()),
            'current_domain': self.current_domain,
            'tasks_executed': len(self.task_history)
        }
