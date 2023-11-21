"""A streamlit page to recommend personal workouts based on the input preferences."""
import os
import sys
import time
import streamlit as st
from pages.settings import (
    page_config,
    custom_css,
    switch_main,
)

# Get the absolute path to the project root directory
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
src_path = os.path.abspath(os.path.join(project_root, "src"))
sys.path.insert(0, src_path)

# Loading prompt templates and GPT Utilities from src
from prompts import recommend_workouts



def workout_recommender():
    """A streamlit function to take the inputs and recommend the workout routine based on the inputs."""

    # Load the page config and custom css from settings
    page_config()
    custom_css()
    switch_main()

    # Define the header for the page
    st.header("Workout Recommendations using GPT 🏋🏻", divider="orange")

    st.info(
        """
            Select the options against each field and click submit to get the customized workout plan for a week.
            """
    )

    workout_plan = ""
    tokens_used = 0
    execution_time = 0.00

    if not st.session_state.valid_key:
        st.warning("Invalid or No OpenAI API Key configured. Please re-configure your OpenAI API Key.")

    col1, col2 = st.columns([0.35, 0.65])

    with col1.form("Fitness_Requirements", clear_on_submit=False):
        Fitness_Goal = st.radio(label="What's your fitness goal?",
                                options=['Build Muscle', 'Lose Weight', 'Improve Endurance', 'Increase Flexibility'],
                                horizontal=True,)
        Fitness_Level = st.radio(label="What's your fitness level?",
                                options=['Beginner', 'Intermediate', 'Advanced', 'Pro-Level'],
                                horizontal=True,)
        Workout_style = st.multiselect(label="What's your preferred workout style?",
                                options=['Weight Lifting 🏋🏻', 'Cardio 🏃🏻‍♂️', 'Yoga 🧘🏻‍♀️', 'Pilates 🤸🏻'],
                                placeholder="Please select your preferred workout styles")
                                # captions=['🏋🏻', '🏃🏻‍♂️', '🧘🏻‍♀️', '🤸🏻'],
                                # horizontal=True,)
        Days_per_week = st.slider(label="How many days do you workout per week?",
                                min_value=1,
                                max_value=7)
        Workout_Location = st.radio(label="Where do you prefer to workout?",
                                options=['Home Only','Gym or Fitness Studio'])
        submit = st.form_submit_button(label="Get the Workout Routine 💪🏻",
                                        disabled=not st.session_state.valid_key)
    
    if submit:
        if len(Workout_style) > 0:
            user_inputs = {
                'fitness_goal': Fitness_Goal,
                'fitness_level': Fitness_Level,
                'workout_style': Workout_style,
                'days_per_week': Days_per_week,
                'workout_location': Workout_Location
            }
            with st.spinner("Building a customized workout plan for you. . ."):

                # Start timer
                start_time = time.time()

                prompt = recommend_workouts(user_inputs=user_inputs)
                gpt_response = st.session_state.gpt.get_completion_from_messages(messages=prompt)
                workout_plan = gpt_response.choices[0].message.content
                tokens_used = gpt_response.usage.total_tokens

                # End timer
                end_time = time.time()

                # Calculate the execution_time
                execution_time = end_time - start_time

                #col2.json(user_inputs)
        else:
            col1.error("You must select minimum one preferred workout style!")

    with col2:
        if len(workout_plan) > 0:
            with st.expander(label="", expanded=True):
                st.markdown("### Workout Plan:")
                st.divider()
                st.write(workout_plan)
                st.markdown(
                    f"<p style='font-size: smaller; color: green;'>Tokens used: {tokens_used}</br>Executed in {execution_time:.4f} seconds",
                    unsafe_allow_html=True,
                )











workout_recommender()