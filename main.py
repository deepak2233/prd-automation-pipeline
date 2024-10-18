import argparse
import logging
from models import BasicNLPModel, AdvancedNLPModel, ReinforcementLearningModel
from utils import PRDIngestionJSON, generate_epics_and_stories, assign_tasks, load_engineers, save_output, perform_eda
from optimization import optimize_workload

# Set up logging to log to a file
logging.basicConfig(filename='pipeline.log', level=logging.INFO, format='%(asctime)s %(levelname)s:%(message)s')

class PRDPipeline:
    def __init__(self, mode='basic', engineer_profiles='data/engineer_profile.json'):
        self.mode = mode
        self.engineers = load_engineers(engineer_profiles)
        self.prd_data = None
        self.model = None

    def load_prd(self, prd_file):
        logging.info("Loading PRD data from JSON file...")
        ingestion = PRDIngestionJSON(prd_file)
        self.prd_data = ingestion.load_prd()

    def initialize_model(self):
        logging.info(f"Initializing NLP model for {self.mode} mode...")
        if self.mode == 'basic':
            self.model = BasicNLPModel()
        elif self.mode == 'advanced':
            self.model = AdvancedNLPModel()
        elif self.mode == 'optimized':
            self.model = ReinforcementLearningModel()
        else:
            raise ValueError(f"Unknown mode: {self.mode}")

    def process_prd(self):
        logging.info(f"Processing PRD for mode: {self.mode}")
        
        # Perform EDA before processing
        logging.info("Performing EDA on PRD and engineer profiles...")
        perform_eda(self.prd_data, self.engineers)

        # Extract sections, generate epics and user stories
        sections = self.model.extract_sections(self.prd_data)
        epics, user_stories = generate_epics_and_stories(sections)

        # Assign tasks based on mode
        if self.mode in ['basic', 'advanced']:
            assignments = assign_tasks(user_stories, self.engineers, mode=self.mode)
        else:
            assignments = self.model.assign_tasks(user_stories, self.engineers)

        return epics, user_stories, assignments

    def optimize_workload(self, assignments):
        logging.info("Optimizing engineer workload...")
        optimized_assignments = optimize_workload(assignments, self.engineers)
        return optimized_assignments

    def run(self, prd_file):
        self.load_prd(prd_file)
        self.initialize_model()
        epics, stories, assignments = self.process_prd()

        if self.mode == 'optimized':
            assignments = self.optimize_workload(assignments)

        # Save output to JSON and Excel files
        logging.info("Saving output to files...")
        save_output(epics, stories, assignments)

        logging.info("Pipeline execution complete.")
        return epics, stories, assignments


if __name__ == "__main__":
    # Argument parsing
    parser = argparse.ArgumentParser(description="PRD Processing Pipeline")
    parser.add_argument("--mode", choices=['basic', 'advanced', 'optimized'], default='basic', help="Pipeline mode: basic, advanced, or optimized.")
    parser.add_argument("--prd_file", required=True, help="Path to the PRD JSON file.")
    parser.add_argument("--engineers", default="data/engineer_profile.json", help="Path to engineer profiles.")
    args = parser.parse_args()

    # Initialize and run the pipeline
    pipeline = PRDPipeline(mode=args.mode, engineer_profiles=args.engineers)
    epics, stories, assignments = pipeline.run(prd_file=args.prd_file)

    # Output results
    logging.info(f"Generated {len(epics)} epics and {len(stories)} user stories.")
    logging.info(f"Assignments: {assignments}")
    print(f"Generated {len(epics)} epics and {len(stories)} user stories.")
    print(f"Assignments: {assignments}")

