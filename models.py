import logging
from sentence_transformers import SentenceTransformer, util

class BasicNLPModel:
    def __init__(self):
        pass

    def extract_sections(self, prd_data):
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

    def assign_tasks(self, stories, engineers):
        assignments = []
        workloads = {eng['name']: 0 for eng in engineers}

        for idx, story in enumerate(stories):
            engineer = engineers[idx % len(engineers)]
            workloads[engineer['name']] += 1
            assignments.append((story, engineer['name']))

        logging.info(f"Basic Mode Task Assignments: {assignments}")
        return assignments

class AdvancedNLPModel:
    def __init__(self):
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

    def extract_sections(self, prd_data):
        return {
            'objectives': prd_data.get('objectives', []),
            'functional_requirements': prd_data.get('functional_requirements', {}),
            'user_personas': prd_data.get('user_personas', [])
        }

    def assign_tasks(self, stories, engineers):
        story_embeddings = self.embedding_model.encode(stories, convert_to_tensor=True)
        engineer_descriptions = [eng['skills'] for eng in engineers]
        engineer_embeddings = self.embedding_model.encode(engineer_descriptions, convert_to_tensor=True)

        assignments = []
        workloads = {eng['name']: 0 for eng in engineers}

        for story, story_embedding in zip(stories, story_embeddings):
            similarities = util.pytorch_cos_sim(story_embedding, engineer_embeddings)[0]
            scores = {eng['name']: similarities[idx].item() / (1 + workloads[eng['name']])
                      for idx, eng in enumerate(engineers)}

            best_engineer = max(scores, key=scores.get)
            workloads[best_engineer] += 1
            assignments.append((story, best_engineer))

        logging.info(f"Advanced Mode Task Assignments: {assignments}")
        return assignments

class ReinforcementLearningModel(AdvancedNLPModel):
    def assign_tasks(self, stories, engineers):
        assignments = super().assign_tasks(stories, engineers)
        logging.info(f"Optimized Mode Task Assignments: {assignments}")
        return assignments
