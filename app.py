import streamlit as st
import pandas as pd
import json
from io import StringIO
from main import PRDPipeline
import os

# Set up the Streamlit app title
st.title("PRD Automation Pipeline")

# Instructions for the user
st.write("Upload your PRD JSON file and Engineer profiles JSON file to process them into Epics, User Stories, and Task Assignments.")

# File uploader for PRD and Engineer Profiles
uploaded_prd_file = st.file_uploader("Upload PRD JSON File", type="json")
uploaded_engineer_file = st.file_uploader("Upload Engineer Profiles JSON File", type="json")

# Dropdown for mode selection (basic, advanced, optimized)
mode = st.selectbox(
    "Select the mode of the pipeline:",
    ("basic", "advanced", "optimized")
)

# Process the uploaded files
if uploaded_prd_file and uploaded_engineer_file:
    # Convert the uploaded PRD JSON file to a usable format
    prd_data = json.load(uploaded_prd_file)
    
    # Convert the uploaded Engineer Profiles JSON file to a usable format
    engineer_data = json.load(uploaded_engineer_file)

    # Write to temp files to simulate file paths
    with open("uploaded_prd.json", "w") as f:
        json.dump(prd_data, f)
    
    with open("uploaded_engineers.json", "w") as f:
        json.dump(engineer_data, f)

    # Run the PRD Pipeline
    st.write(f"Processing the PRD and Engineer Profiles in **{mode}** mode...")

    # Initialize and run the pipeline based on the selected mode
    pipeline = PRDPipeline(mode=mode, engineer_profiles="uploaded_engineers.json")
    epics, stories, assignments = pipeline.run(prd_file="uploaded_prd.json")
    
    # Display results
    st.success("Processing complete!")
    
    # Show Epics
    st.header("Generated Epics")
    st.write(pd.DataFrame(epics, columns=["Epics"]))

    # Show User Stories
    st.header("Generated User Stories")
    st.write(pd.DataFrame(stories, columns=["User Stories"]))

    # Show Task Assignments
    st.header("Task Assignments to Engineers")
    df_assignments = pd.DataFrame(assignments, columns=["User Story", "Assigned Engineer"])
    st.write(df_assignments)

    # Allow users to download the output as JSON and Excel
    st.download_button(
        label="Download Results as JSON",
        data=json.dumps({
            "epics": epics,
            "user_stories": stories,
            "assignments": assignments
        }, indent=4),
        file_name="output_results.json",
        mime="application/json"
    )
    
    # Save output to Excel and offer for download
    excel_file = "output_results.xlsx"
    df_epics = pd.DataFrame(epics, columns=["Epics"])
    df_stories = pd.DataFrame(stories, columns=["User Stories"])
    df_assignments = pd.DataFrame(assignments, columns=["User Story", "Assigned Engineer"])

    with pd.ExcelWriter(excel_file, engine='xlsxwriter') as writer:
        df_epics.to_excel(writer, sheet_name='Epics', index=False)
        df_stories.to_excel(writer, sheet_name='User Stories', index=False)
        df_assignments.to_excel(writer, sheet_name='Assignments', index=False)

    with open(excel_file, 'rb') as f:
        st.download_button(
            label="Download Results as Excel",
            data=f,
            file_name="output_results.xlsx",
            mime="application/vnd.ms-excel"
        )

else:
    st.warning("Please upload both a PRD JSON file and an Engineer Profiles JSON file to continue.")

