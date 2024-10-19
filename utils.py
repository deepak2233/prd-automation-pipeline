import json
import pandas as pd
import logging
import matplotlib.pyplot as plt
import numpy as np
from sklearn.metrics import precision_score, recall_score, f1_score
from nltk.translate.bleu_score import sentence_bleu
from rouge_score import rouge_scorer
from sentence_transformers import SentenceTransformer, util

class PRDIngestionJSON:
    def __init__(self, prd_file):
        self.prd_file = prd_file

    def load_prd(self):
        with open(self.prd_file, 'r') as file:
            return json.load(file)

def load_engineers(engineer_profiles):
    with open(engineer_profiles, 'r') as file:
        return json.load(file)

def generate_epics_and_stories(sections):
    epics = []
    user_stories = []
    functional_requirements = sections.get('functional_requirements', {})

    for epic, requirements in functional_requirements.items():
        epics.append(f"Epic: {epic}")
        for req in requirements:
            user_story = f"As a user, I want {req} so that I can improve productivity."
            user_stories.append(user_story)

    return epics, user_stories

def save_output(epics, user_stories, assignments, file_prefix='output'):
    output_data = {
        'epics': epics,
        'user_stories': user_stories,
        'assignments': assignments
    }

    json_file = f"{file_prefix}.json"
    with open(json_file, 'w') as json_outfile:
        json.dump(output_data, json_outfile, indent=4)

    df_epics = pd.DataFrame(epics, columns=['Epics'])
    df_stories = pd.DataFrame(user_stories, columns=['User Stories'])
    df_assignments = pd.DataFrame(assignments, columns=['User Story', 'Assigned Engineer'])

    excel_file = f"{file_prefix}.xlsx"
    with pd.ExcelWriter(excel_file, engine='xlsxwriter') as writer:
        df_epics.to_excel(writer, sheet_name='Epics', index=False)
        df_stories.to_excel(writer, sheet_name='User Stories', index=False)
        df_assignments.to_excel(writer, sheet_name='Assignments', index=False)

def evaluate_assignments(assignments, engineers, sections, prd_data):
    evaluation_results = {}

    skill_scores = []
    for story, engineer in assignments:
        task_embedding = util.pytorch_cos_sim(
            SentenceTransformer('all-MiniLM-L6-v2').encode(story, convert_to_tensor=True),
            SentenceTransformer('all-MiniLM-L6-v2').encode(engineers[0]['skills'], convert_to_tensor=True)
        )
        skill_scores.append(task_embedding.item())
    skill_match_score = np.mean(skill_scores)
    evaluation_results["Skill Match Score"] = skill_match_score

    engineer_workloads = {eng['name']: 0 for eng in engineers}
    for _, engineer in assignments:
        engineer_workloads[engineer] += 1
    workload_variance = np.var(list(engineer_workloads.values()))
    evaluation_results["Workload Variance"] = workload_variance

    sorted_workloads = sorted(engineer_workloads.values())
    n = len(sorted_workloads)
    gini = (2 * sum((i + 1) * wl for i, wl in enumerate(sorted_workloads)) / (n * sum(sorted_workloads))) - (n + 1) / n
    evaluation_results["Gini Coefficient of Workload"] = gini

    reference_sections = [' '.join(sections['objectives']), ' '.join(sections['user_personas'])]
    predicted_sections = [' '.join(prd_data.get('objectives', [])), ' '.join(prd_data.get('user_personas', []))]
    bleu_score = np.mean([sentence_bleu([ref.split()], pred.split()) for ref, pred in zip(reference_sections, predicted_sections)])
    evaluation_results["BLEU Score"] = bleu_score

    rouge_scorer_instance = rouge_scorer.RougeScorer(['rouge1', 'rouge2', 'rougeL'], use_stemmer=True)
    rouge_scores = [rouge_scorer_instance.score(ref, pred) for ref, pred in zip(reference_sections, predicted_sections)]
    avg_rouge_score = np.mean([score['rouge1'].fmeasure for score in rouge_scores])
    evaluation_results["ROUGE Score"] = avg_rouge_score

    semantic_sim_model = SentenceTransformer('all-MiniLM-L6-v2')
    ref_embeddings = semantic_sim_model.encode(reference_sections, convert_to_tensor=True)
    pred_embeddings = semantic_sim_model.encode(predicted_sections, convert_to_tensor=True)
    semantic_sim_score = np.mean(util.pytorch_cos_sim(ref_embeddings, pred_embeddings).diagonal().tolist())
    evaluation_results["Semantic Similarity Score"] = semantic_sim_score

    return evaluation_results

def perform_eda(prd_data, engineers):
    logging.info("Performing EDA...")
    product_name = prd_data.get('product_name', 'N/A')
    objectives = len(prd_data.get('objectives', []))
    functional_areas = len(prd_data.get('functional_requirements', {}))
    engineer_count = len(engineers)
    roles = [eng['role'] for eng in engineers]

    plt.figure(figsize=(10, 6))
    plt.bar(['Objectives', 'Functional Areas'], [objectives, functional_areas], color='purple')
    plt.title(f'PRD Overview for {product_name}')
    plt.xlabel('Categories')
    plt.ylabel('Count')
    plt.savefig('eda_prd_overview.png')
    logging.info("Saved EDA plot as eda_prd_overview.png")

    plt.figure(figsize=(10, 6))
    plt.barh(roles, range(1, len(roles) + 1), color='green')
    plt.title('Engineer Roles Distribution')
    plt.xlabel('Role')
    plt.ylabel('Count')
    plt.savefig('eda_engineer_roles.png')
    logging.info("Saved EDA plot as eda_engineer_roles.png")
