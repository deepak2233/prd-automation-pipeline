import logging
from transformers import pipeline
from sentence_transformers import SentenceTransformer, util

class BasicNLPModel:
    def __init__(self):
        pass

    def extract_sections(self, prd_data):
        """
        Basic section extraction from structured JSON.
        """
        objectives = prd_data.get('objectives', [])
        functional_requirements = prd_data.get('functional_requirements', {})
        user_personas = prd_data.get('user_personas', [])
        
        sections = {
            'objectives': objectives,
            'functional_requirements': functional_requirements,
            'user_personas': user_personas
        }
        logging.info("Extracted sections: Objectives, Functional Requirements, User Personas")
        return sections


class AdvancedNLPModel:
    def __init__(self):
        self.qa_model = pipeline('question-answering')

    def extract_sections(self, prd_data):
        """
        Advanced section extraction using transformers.
        """
        objectives = prd_data.get('objectives', [])
        functional_requirements = prd_data.get('functional_requirements', {})
        sections = {
            'objectives': objectives,
            'functional_requirements': functional_requirements
        }
        return sections


class ReinforcementLearningModel:
    def __init__(self):
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

    def extract_sections(self, prd_data):
        """
        Reinforcement learning-based section extraction.
        """
        return prd_data

    def assign_tasks(self, stories, engineers):
        """
        Use semantic similarity to assign tasks intelligently.
        """
        story_embeddings = self.embedding_model.encode(stories, convert_to_tensor=True)
        engineer_descriptions = [engineer['skills'] for engineer in engineers]
        engineer_embeddings = self.embedding_model.encode(engineer_descriptions, convert_to_tensor=True)

        task_assignments = []
        for story, story_embedding in zip(stories, story_embeddings):
            similarities = util.pytorch_cos_sim(story_embedding, engineer_embeddings)
            best_engineer_idx = similarities.argmax()
            best_engineer = engineers[best_engineer_idx]['name']
            task_assignments.append((story, best_engineer))

        return task_assignments

