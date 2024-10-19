import streamlit as st
from utils import generate_epics_and_stories, save_output, perform_eda, evaluate_assignments
from models import BasicNLPModel, AdvancedNLPModel, ReinforcementLearningModel
from optimization import optimize_workload_knapsack
import json
import pandas as pd

def run_app():
    st.title("PRD Automation Pipeline")
    st.write("Upload your PRD JSON file and Engineer profiles JSON file to process them into Epics, User Stories, and Task Assignments.")

    # File upload components
    prd_file = st.file_uploader("Upload PRD JSON File", type=["json"])
    engineer_file = st.file_uploader("Upload Engineer Profiles JSON File", type=["json"])

    if prd_file and engineer_file:
        prd_data = json.load(prd_file)
        engineers = json.load(engineer_file)

        # Pipeline mode selection
        mode = st.selectbox("Select the mode of the pipeline:", ["basic", "advanced", "optimized"])

        if st.button("Run Pipeline"):
            st.info(f"Processing the PRD and Engineer Profiles in {mode} mode...")

            # Initialize the model based on the selected mode
            if mode == "basic":
                nlp_model = BasicNLPModel()
            elif mode == "advanced":
                nlp_model = AdvancedNLPModel()
            else:
                nlp_model = ReinforcementLearningModel()

            # Extract PRD sections
            sections = nlp_model.extract_sections(prd_data)

            # Generate epics and user stories
            epics, user_stories = generate_epics_and_stories(sections)

            # Task assignment based on mode
            if mode == 'optimized':
                initial_assignments = nlp_model.assign_tasks(user_stories, engineers)
                assignments = optimize_workload_knapsack(initial_assignments, engineers)
            else:
                assignments = nlp_model.assign_tasks(user_stories, engineers)

            # Display generated epics and user stories in tables
            st.subheader("Generated Epics")
            epics_df = pd.DataFrame(epics, columns=["Epics"])
            st.dataframe(epics_df, height=200)

            st.subheader("Generated User Stories")
            stories_df = pd.DataFrame(user_stories, columns=["User Stories"])
            st.dataframe(stories_df, height=300)

            st.subheader("Task Assignments")
            assignments_df = pd.DataFrame(assignments, columns=["User Story", "Assigned Engineer"])
            st.dataframe(assignments_df, height=300)

            # Provide download options for JSON and CSV outputs
            json_output = json.dumps({'epics': epics, 'user_stories': user_stories, 'assignments': assignments}, indent=4)
            csv_output = assignments_df.to_csv(index=False)

            st.download_button("Download JSON", data=json_output, file_name='output.json', mime='application/json')
            st.download_button("Download CSV", data=csv_output, file_name='output.csv', mime='text/csv')

            # Evaluate task assignments
            evaluation_results = evaluate_assignments(assignments, engineers, sections, prd_data)
            st.subheader("Evaluation Metrics")
            eval_df = pd.DataFrame(list(evaluation_results.items()), columns=['Metric', 'Value'])
            st.bar_chart(eval_df.set_index('Metric'))

            # Perform EDA and show images
            st.subheader("Exploratory Data Analysis (EDA)")
            perform_eda(prd_data, engineers)
            st.image('eda_prd_overview.png', caption='PRD Overview')
            st.image('eda_engineer_roles.png', caption='Engineer Roles Distribution')

if __name__ == "__main__":
    run_app()
