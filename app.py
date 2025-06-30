import streamlit as st
import google.generativeai as genai
import os
import re

# -------------------------------
# Page Configuration
# -------------------------------
st.set_page_config(
    page_title="YouTube Title & Description Generator",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------------------
# Gemini API Setup
# -------------------------------
def get_gemini_api_key():
    return st.secrets.get("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY")

api_key = get_gemini_api_key()

if not api_key:
    st.error("Gemini API key not found. Please add it to .streamlit/secrets.toml.")
    st.stop()

genai.configure(api_key=api_key)

# ✅ FIXED: Use the correct model name for current Gemini API
model = genai.GenerativeModel("gemini-1.5-flash")

# -------------------------------
# Prompt Templates
# -------------------------------
def create_title_prompt(content, video_type, target_audience, keywords, tone):
    return f"""You are a YouTube SEO expert. Generate 5 compelling, click-worthy titles for a {video_type} video targeting {target_audience}.

Content Summary: {content}

Requirements:
- Keywords: {keywords}
- Tone: {tone}
- 40–70 characters
- Curiosity, urgency, power words (but not clickbait)

List the 5 titles numbered 1 to 5.
"""

def create_description_prompt(content, video_type, target_audience, keywords, channel_info):
    return f"""You are a YouTube SEO specialist. Write a 200–500 word SEO-optimized description for a {video_type} video targeting {target_audience}.

Summary: {content}
Channel Info: {channel_info}
Target Keywords: {keywords}

Include:
- Strong opening sentence
- 2–3 hashtags
- A call-to-action
- Timestamp placeholders if needed
"""

def create_tags_prompt(content, video_type, keywords):
    return f"""Suggest 12–15 YouTube tags (comma-separated) for a {video_type} video.

Video Summary: {content}
Keywords: {keywords}
"""

# -------------------------------
# Gemini Content Generation
# -------------------------------
def call_gemini(prompt):
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"Error calling Gemini: {str(e)}"

# -------------------------------
# Utils
# -------------------------------
def extract_titles(response):
    lines = response.split('\n')
    titles = []
    for line in lines:
        if re.match(r'^\d+\.', line.strip()):
            titles.append(line.split('.', 1)[1].strip())
    return titles[:5]

def extract_tags(response):
    return [tag.strip() for tag in re.split(r'[;,|]+', response) if 2 < len(tag.strip()) < 30][:15]

# -------------------------------
# Session State
# -------------------------------
if 'titles' not in st.session_state:
    st.session_state.titles = []
if 'description' not in st.session_state:
    st.session_state.description = ""
if 'tags' not in st.session_state:
    st.session_state.tags = []

# -------------------------------
# UI Layout
# -------------------------------
st.title("🧠 YouTube Title & Description Generator (Gemini)")

video_script = st.text_area("Video Script or Summary", height=200)
video_type = st.selectbox("Video Type", ["Tutorial", "Review", "Entertainment", "Educational", "Other"])
target_audience = st.selectbox("Target Audience", ["General", "Beginners", "Professionals", "Other"])
keywords = st.text_input("Target Keywords (comma-separated)")
channel_info = st.text_area("Channel Info (optional)", height=80)
tone = st.selectbox("Tone", ["Professional", "Casual", "Energetic", "Educational"])

generate_titles = st.checkbox("Generate Titles", True)
generate_desc = st.checkbox("Generate Description", True)
generate_tag = st.checkbox("Generate Tags", True)

if st.button("Generate"):
    if not video_script.strip():
        st.error("Please provide the video script or summary.")
    else:
        if generate_titles:
            prompt = create_title_prompt(video_script, video_type, target_audience, keywords, tone)
            response = call_gemini(prompt)
            st.session_state.titles = extract_titles(response)
        if generate_desc:
            prompt = create_description_prompt(video_script, video_type, target_audience, keywords, channel_info)
            st.session_state.description = call_gemini(prompt)
        if generate_tag:
            prompt = create_tags_prompt(video_script, video_type, keywords)
            st.session_state.tags = extract_tags(call_gemini(prompt))

# -------------------------------
# Display Output
# -------------------------------
if st.session_state.titles:
    st.subheader("📝 Titles")
    for t in st.session_state.titles:
        st.write(f"- {t}")

if st.session_state.description:
    st.subheader("📄 Description")
    st.text_area("", st.session_state.description, height=200)

if st.session_state.tags:
    st.subheader("🏷️ Tags")
    st.write(", ".join(st.session_state.tags))