import streamlit as st
import csv
import io
import random

# ------------------------------
# VECTOR MINDSET TIPS
# ------------------------------
MINDSET_TIPS = [
    "Consistency beats intensity.",
    "Focus on the next right step, not the next twelve.",
    "Build the habit, then build the volume.",
    "Progress is better than perfection.",
    "Small, steady gains stack into big results."
]

def get_random_tip():
    return random.choice(MINDSET_TIPS)

# ------------------------------
# WORKOUT DETAILS
# ------------------------------
WORKOUT_DETAILS = {
    "Easy Run": "Easy Run: 30-40 min easy jog, maintain conversational pace",
    "Speed Work": "Speed Work: 20-30 min intervals, 1-2 min fast / 1-2 min easy recovery",
    "Long Run": "Long Run: 60-90 min steady pace, build endurance",
    "Lift": "Lift: Upper or Lower or Full-body split, 3-4 exercises, moderate weights",
    "Total Body Lift": "Total Body Lift: 1 set each of push, pull, legs, core, light weights",
    "Zone 2": "Zone 2 Cardio: 20-50 min easy steady state (walk, bike, jog)",
    "Optional Zone 2": "Optional Zone 1/2 Cardio: 20-40 min easy walking or light movement",
    "Optional Recovery": "Optional Recovery: mobility work, stretching, or light walk"
}

# ------------------------------
# WEEK TEMPLATES BASED ON EXPERIENCE
# ------------------------------
WORKOUT_TEMPLATES = {
    "beginner": ["Easy Run", "Total Body Lift", "Zone 2", "Optional Recovery"],
    "intermediate": ["Lift", "Run", "Lift", "Run", "Optional Zone 2"],
    "advanced": ["Lift", "Run", "Lift", "Run", "Lift", "Zone 2"]
}

DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

# ------------------------------
# GOAL ADJUSTMENTS
# ------------------------------
def adjust_for_goal(template, experience, goal):
    template = template.copy()

    # Advanced hybrid run assignment
    if goal == "hybrid" and experience == "advanced":
        run_days = [i for i, w in enumerate(template) if "Run" in w]
        for idx, run_idx in enumerate(run_days):
            if idx == 0:
                template[run_idx] = "Easy Run"
            elif idx == 1:
                template[run_idx] = "Speed Work"
            else:
                template[run_idx] = "Long Run"
        return template[:len(template)]

    # Intermediate running goal: 2 easy runs + 1 long run
    if goal == "running" and experience == "intermediate":
        run_days = [i for i, w in enumerate(template) if "Run" in w]
        for idx, run_idx in enumerate(run_days):
            if idx < 2:
                template[run_idx] = "Easy Run"
            else:
                template[run_idx] = "Long Run"
        return template[:len(template)]

    # Beginner running goal
    if goal == "running" and experience == "beginner":
        return ["Easy Run (Longer)" if "Easy Run" in x else x for x in template]

    # Strength goal adjustments
    if goal == "strength":
        template = ["Lift" if "Run" in x else x for x in template]

    # Other running/hybrid adjustments
    if goal in ["running", "hybrid"] and experience == "advanced":
        for i, w in enumerate(template):
            if w == "Run":
                template[i] = "Easy Run"

    return template

# ------------------------------
# BUILD WEEKLY SCHEDULE
# ------------------------------
def build_weekly_schedule(template, days_available):
    schedule = {}
    training_days = days_available
    rest_days = 7 - training_days
    total_days = 7

    spacing = total_days / rest_days if rest_days > 0 else total_days + 1
    template_index = 0
    rest_counter = spacing / 2  # start somewhere in the middle

    for i, day in enumerate(DAYS):
        if rest_days > 0 and i >= rest_counter:
            schedule[day] = WORKOUT_DETAILS.get("Optional Recovery", "Rest / Optional Recovery")
            rest_days -= 1
            rest_counter += spacing
        else:
            workout = template[template_index % len(template)]
            schedule[day] = WORKOUT_DETAILS.get(workout, workout)
            template_index += 1

    return schedule

# ------------------------------
# ASSIGN SPECIFIC LIFT TYPES
# ------------------------------
def assign_lift_details(schedule, goal):
    lift_days = [day for day, workout in schedule.items() if "Lift" in workout]
    num_lifts = len(lift_days)

    lift_plan = []
    if num_lifts <= 2:
        lift_plan = ["Full Body"] * num_lifts
    elif num_lifts == 3 and goal == "running":
        lift_plan = ["Upper Body", "Lower Body", "Upper Body"]
    elif num_lifts == 4 and goal == "strength":
        lift_plan = ["Upper Body", "Lower Body", "Upper Body", "Lower Body"]
    else:
        lift_plan = ["Full Body"] * num_lifts

    for i, day in enumerate(lift_days):
        lift_type = lift_plan[i % len(lift_plan)]
        schedule[day] = f"Lift: {lift_type}, 3-4 exercises, moderate weights"

    return schedule

# ------------------------------
# STREAMLIT APP
# ------------------------------
st.title("Vector Weekly Training Plan Generator")
st.write("Generate a personalized weekly schedule based on your experience and goals.")

# User inputs
experience = st.selectbox("Experience Level", ["beginner", "intermediate", "advanced"])

# Days available slider based on experience
days_options = {
    "beginner": (3,4),
    "intermediate": (4,5),
    "advanced": (5,6)
}
days_available = st.slider(
    "Days you can train per week",
    min_value=days_options[experience][0],
    max_value=days_options[experience][1],
    value=days_options[experience][0]
)

goal = st.selectbox("Training Goal", ["general", "hybrid", "running", "strength"])

# Generate schedule
if st.button("Generate Schedule"):
    base_template = WORKOUT_TEMPLATES[experience]
    adjusted_template = adjust_for_goal(base_template, experience, goal)
    weekly_schedule = build_weekly_schedule(adjusted_template, days_available)
    weekly_schedule = assign_lift_details(weekly_schedule, goal)

    # Display schedule
    st.subheader("Your Weekly Schedule")
    schedule_text = "\n".join([f"{day}: {workout}" for day, workout in weekly_schedule.items()])
    st.text_area("Schedule", schedule_text, height=300)

    # Prepare CSV for download
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Day", "Workout"])
    for day, workout in weekly_schedule.items():
        writer.writerow([day, workout])
    writer.writerow([])
    writer.writerow(["Mindset Tip", random.choice(MINDSET_TIPS)])
    st.download_button("Download CSV", output.getvalue(), file_name="weekly_plan.csv")
