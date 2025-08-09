import streamlit as st
import pandas as pd
import numpy as np

# --- 1) Small job bank (skills + base salary) ---
job_bank = {
    "Data Scientist": {
        "skills": ["python","pandas","numpy","ml","sql"],
        "base_salary": 60000
    },
    "ML Engineer": {
        "skills": ["python","pytorch","tensorflow","ml","docker"],
        "base_salary": 65000
    },
    "Frontend Developer": {
        "skills": ["javascript","react","css","html"],
        "base_salary": 45000
    },
    "Backend Developer": {
        "skills": ["python","django","sql","docker"],
        "base_salary": 55000
    }
}

# --- 2) helper functions ---
def preprocess_skill_text(text):
    # turn input into lower-case tokens
    return [t.strip().lower() for t in text.replace(",", " ").split() if t.strip()]

def match_score(user_skills, job_skills):
    # fraction of job skills the user has
    s_user = set(user_skills)
    s_job = set(job_skills)
    if len(s_job) == 0:
        return 0.0
    matched = len(s_user & s_job)
    return matched / len(s_job)

def estimate_salary(base_salary, match, years_exp, certs):
    multiplier = 1 + match * 0.25 + years_exp * 0.03 + certs * 0.01
    return base_salary * multiplier

# --- 3) Streamlit UI ---
st.title("Job Role Matcher + Salary Estimator (simple demo)")
st.write("Type your skills (space or comma separated), years of experience and number of certifications.")

skills_input = st.text_input("Your skills (example: python pandas sql ml)", value="python pandas")
years = st.number_input("Years of experience", min_value=0, max_value=40, value=1)
certs = st.number_input("Number of certifications", min_value=0, max_value=10, value=0)

if st.button("Find jobs"):
    user_skills = preprocess_skill_text(skills_input)
    results = []
    for role, info in job_bank.items():
        job_sk = info["skills"]
        base = info["base_salary"]
        m = match_score(user_skills, job_sk)
        est = estimate_salary(base, m, years, certs)
        results.append({
            "role": role,
            "match_percent": f"{m*100:.0f}%",
            "base_salary": base,
            "estimated_salary": int(est),
            "missing_skills": list(set(job_sk) - set(user_skills))
        })
    df = pd.DataFrame(results).sort_values("estimated_salary", ascending=False)
    st.subheader("Top role suggestions")
    st.dataframe(df)

    # Recommend skills: for the best role, show marginal gains from adding each missing skill
    top_role = df.iloc[0]
    st.subheader(f"Recommendations for: {top_role.role}")
    missing = top_role.missing_skills
    gains = []
    base = top_role.base_salary
    current_match = float(top_role.match_percent.strip("%"))/100
    for s in missing:
        new_skills = set(user_skills) | {s}
        new_match = match_score(list(new_skills), job_bank[top_role.role]["skills"])
        new_est = estimate_salary(base, new_match, years, certs)
        gains.append((s, int(new_est - top_role.estimated_salary)))
    gains_sorted = sorted(gains, key=lambda x: x[1], reverse=True)
    st.write("Top skills to add (estimated salary gain):")
    for skill, gain in gains_sorted[:3]:
        st.write(f"- {skill} → +{gain} ({'+' if gain>=0 else ''}{gain})")
