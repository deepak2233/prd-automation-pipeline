import json
import pandas as pd
import logging
import matplotlib.pyplot as plt

class PRDIngestionJSON:
    def __init__(self, prd_file):
        self.prd_file = prd_file

    def load_prd(self):
        """
        Load the PRD data from a JSON file.
        
        
        """
        try:
            with open(self.prd_file, 'r') as file:
                prd_data = json.load(file)
            logging.info(f"Successfully loaded PRD data from {self.prd_file}")
            return prd_data
        except Exception as e:
            logging.error(f"Error loading PRD file {self.prd_file}: {str(e)}")
            raise e

def load_engineers(engineer_profiles):
    """
    Load engineer profiles from a JSON file.
    """
    try:
        with open(engineer_profiles, 'r') as file:
            engineers = json.load(file)
        logging.info(f"Successfully loaded engineer profiles from {engineer_profiles}")
        return engineers
    except Exception as e:
        logging.error(f"Error loading engineer profiles from {engineer_profiles}: {str(e)}")
        raise e

def generate_epics_and_stories(sections):
    """
    Generate epics and user stories from the functional requirements.
    """
    epics = []
    user_stories = []
    functional_requirements = sections.get('functional_requirements', {})

    for epic, requirements in functional_requirements.items():
        epics.append(f"Epic: {epic}")
        for req in requirements:
            user_story = f"As a user, I want {req} so that I can improve productivity."
            user_stories.append(user_story)

    logging.info(f"Generated {len(epics)} epics and {len(user_stories)} user stories.")
    return epics, user_stories

def assign_tasks(stories, engineers, mode='basic'):
    """
    Assign tasks (user stories) to engineers based on the mode.
    For 'basic' mode, a simple round-robin assignment is used.
    """
    assignments = []
    if mode == 'basic':
        # Round-robin assignment of user stories to engineers
        logging.info("Assigning tasks in basic mode using round-robin assignment.")
        for i, story in enumerate(stories):
            engineer = engineers[i % len(engineers)]['name']
            assignments.append((story, engineer))
    elif mode == 'advanced':
        # More advanced role-based assignment could be implemented here
        logging.info("Assigning tasks in advanced mode.")
        for i, story in enumerate(stories):
            engineer = engineers[i % len(engineers)]['name']
            assignments.append((story, engineer))
    logging.info(f"Assigned {len(assignments)} tasks to engineers.")
    return assignments

def save_output(epics, user_stories, assignments, file_prefix='output'):
    """
    Save epics, user stories, and assignments to JSON and Excel files.
    """
    output_data = {
        'epics': epics,
        'user_stories': user_stories,
        'assignments': assignments
    }

    try:
        # Save to JSON
        json_file = f"{file_prefix}.json"
        with open(json_file, 'w') as json_outfile:
            json.dump(output_data, json_outfile, indent=4)
        logging.info(f"Output successfully saved to {json_file}")

        # Save to Excel
        excel_file = f"{file_prefix}.xlsx"
        df_epics = pd.DataFrame(epics, columns=['Epics'])
        df_stories = pd.DataFrame(user_stories, columns=['User Stories'])
        df_assignments = pd.DataFrame(assignments, columns=['User Story', 'Assigned Engineer'])

        with pd.ExcelWriter(excel_file, engine='xlsxwriter') as writer:
            df_epics.to_excel(writer, sheet_name='Epics', index=False)
            df_stories.to_excel(writer, sheet_name='User Stories', index=False)
            df_assignments.to_excel(writer, sheet_name='Assignments', index=False)

        logging.info(f"Output successfully saved to {excel_file}")
    except Exception as e:
        logging.error(f"Error saving output: {str(e)}")
        raise e

def perform_eda(prd_data, engineers):
    """
    Perform basic exploratory data analysis (EDA) on the PRD and engineer profiles.
    """
    try:
        logging.info("Performing EDA on PRD...")
        product_name = prd_data.get('product_name', 'N/A')
        objectives = len(prd_data.get('objectives', []))
        functional_areas = len(prd_data.get('functional_requirements', {}))

        logging.info(f"Product Name: {product_name}")
        logging.info(f"Number of Objectives: {objectives}")
        logging.info(f"Functional Areas: {functional_areas}")

        # Plot objectives
        plt.figure(figsize=(6, 4))
        plt.bar(['Objectives'], [objectives], color='blue')
        plt.title('Number of Objectives')
        plt.savefig('eda_objectives.png')
        logging.info("Saved EDA plot for objectives as eda_objectives.png")

        # Engineer Profile EDA
        logging.info("Performing EDA on Engineer Profiles...")
        engineer_count = len(engineers)
        logging.info(f"Number of Engineers: {engineer_count}")
        roles = [engineer['role'] for engineer in engineers]

        # Plot engineer roles
        plt.figure(figsize=(6, 4))
        plt.barh(roles, range(1, len(roles)+1), color='green')
        plt.title('Engineer Roles')
        plt.savefig('eda_engineer_roles.png')
        logging.info("Saved EDA plot for engineer roles as eda_engineer_roles.png")
    except Exception as e:
        logging.error(f"Error during EDA: {str(e)}")
        raise e

