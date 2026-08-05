"""
Self Trainer
============

Trains the AI agent through experience and feedback.
"""

class SelfTrainer:
    """Self-training system"""
    
    def __init__(self, memory):
        self.memory = memory
        self.experience_count = 0
    
    def learn_from_experience(self, experience: str, success: bool) -> None:
        """Learn from experience"""
        self.experience_count += 1
        self.memory.add_experience(
            action=experience,
            result="Learned from experience",
            context="self_training",
            success=success
        )
    
    def get_summary(self) -> dict:
        """Get training summary"""
        return {'experience_count': self.experience_count}
