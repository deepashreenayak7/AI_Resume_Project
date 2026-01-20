import streamlit as st
import pdfplumber
import re
import altair as alt
import pandas as pd


SKILLS_DB = [
    "python","sql","java","c","c++","machine learning","deep learning",
    "tensorflow","keras","pandas","numpy","excel","power bi",
    "html","css","javascript","react","git","github",
    "statistics","data analysis","nlp","flask","streamlit",
    "communication","problem solving","linux","mysql","postgresql",
    "networking","troubleshooting","data structures","algorithms"
]


def extract_text(pdf):
    text = ""
    with pdfplumber.open(pdf) as pdf_file:
        for page in pdf_file.pages:
            if page.extract_text():
                text += page.extract_text() + " "
    return text

def clean_text(text):
    text = text.lower()
    text = re.sub('[^a-z ]',' ',text)
    text = re.sub('\s+',' ',text)
    return text

def extract_skills(text):
    found = []
    for skill in SKILLS_DB:
        pattern = r"\b" + re.escape(skill) + r"\b"
        if re.search(pattern, text):
            found.append(skill)
    return sorted(list(set(found)))

def ats_score(resume_skills, jd_skills):
    if not jd_skills:
        return 0
    matched = [s for s in jd_skills if s in resume_skills]
    return round(len(matched)/len(jd_skills)*100,2)

st.set_page_config(page_title="AI Resume Screening System")
st.title("🚀 AI Resume Screening & Job Recommendation System")
st.write("Upload your resume and paste a job description to analyze skills, ATS score, and skill gaps.")

resume_file = st.file_uploader("Upload Resume PDF", type=["pdf"])
job_desc = st.text_area("Paste Job Description")

resume_skills = []
job_skills = []
matched = []
missing = []
ats = 0

if resume_file:
    resume_text = extract_text(resume_file)
    resume_clean = clean_text(resume_text)
    resume_skills = extract_skills(resume_clean)
    if resume_skills:
        st.subheader("📄 Resume Skills Found")
        st.write(resume_skills)
    else:
        st.warning("⚠ No skills detected in your resume. Make sure your resume mentions technical skills clearly.")

if job_desc:
    job_clean = clean_text(job_desc)
    job_skills = extract_skills(job_clean)
    if job_skills:
        st.subheader("💼 Job Description Skills Found")
        st.write(job_skills)
    else:
        st.warning("⚠ No skills detected in the Job Description. ATS score cannot be calculated.")


if resume_file and job_desc:
    matched = [s for s in job_skills if s in resume_skills]
    missing = [s for s in job_skills if s not in resume_skills]
    ats = ats_score(resume_skills, job_skills)

    st.subheader("📊 Matching Result")
    
    if matched:
        st.success("✅ Matched Skills:")
        st.write(matched)
    else:
        st.info("ℹ No matched skills detected.")
    
    if missing:
        st.error("❌ Missing Skills (Add these to improve your resume):")
        st.write(missing)
    else:
        st.info("🎉 No missing skills detected!")

    st.metric("📌 ATS Score", f"{ats} %")


if resume_file and job_desc:
    data = pd.DataFrame({
        "Category": ["Matched Skills","Missing Skills"],
        "Count": [len(matched), len(missing)]
    })
    chart = alt.Chart(data).mark_bar().encode(
        x='Category',
        y='Count',
        color=alt.condition(
            alt.datum.Category == 'Matched Skills',
            alt.value('green'),
            alt.value('red')
        )
    ).properties(
        title='Skill Gap Dashboard'
    )
    st.subheader("📈 Skill Gap Dashboard")
    st.altair_chart(chart, use_container_width=True)


if resume_file and missing:
    st.subheader("💡 Resume Improvement Suggestions")
    for skill in missing:
        st.write(f"- Add experience/project mentioning **{skill}**")
