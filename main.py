import argparse
import logging
from utils import PRDIngestionJSON, load_engineers, generate_epics_and_stories, save_output, perform_eda, evaluate_assignments
from models import BasicNLPModel, AdvancedNLPModel, ReinforcementLearningModel
from optimization import optimize_workload_knapsack

logging.basicConfig(filename='pipeline.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def main():
    parser = argparse.ArgumentParser(description='PRD Automation Pipeline')
    parser.add_argument('--mode', type=str, choices=['basic', 'advanced', 'optimized'], required=True,
                        help='Mode to run the pipeline: basic, advanced, or optimized')
    parser.add_argument('--prd_file', type=str, required=True, help='Path to the PRD JSON file')
    parser.add_argument('--engineers', type=str, required=True, help='Path to the Engineer Profiles JSON file')

    args = parser.parse_args()

    prd_data_loader = PRDIngestionJSON(args.prd_file)
    prd_data = prd_data_loader.load_prd()

    engineers = load_engineers(args.engineers)

    if args.mode == 'basic':
        nlp_model = BasicNLPModel()
    elif args.mode == 'advanced':
        nlp_model = AdvancedNLPModel()
    else:
        nlp_model = ReinforcementLearningModel()

    sections = nlp_model.extract_sections(prd_data)
    epics, user_stories = generate_epics_and_stories(sections)

    if args.mode == 'optimized':
        initial_assignments = nlp_model.assign_tasks(user_stories, engineers)
        assignments = optimize_workload_knapsack(initial_assignments, engineers)
    else:
        assignments = nlp_model.assign_tasks(user_stories, engineers)

    save_output(epics, user_stories, assignments)

    evaluation_results = evaluate_assignments(assignments, engineers, sections, prd_data)
    logging.info(f"Evaluation Results: {evaluation_results}")

    perform_eda(prd_data, engineers)

if __name__ == "__main__":
    main()
