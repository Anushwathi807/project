import os
import json
import google.generativeai as genai

genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

def build_prompt(data):
    gh = data["github"]
    lc = data["leetcode"]
    kg = data["kaggle"]

    lc_total = lc["stats"]["acSubmissionNum"][0]["count"]
    lc_easy = lc["stats"]["acSubmissionNum"][1]["count"]
    lc_medium = lc["stats"]["acSubmissionNum"][2]["count"]
    lc_hard = lc["stats"]["acSubmissionNum"][3]["count"]

    prompt = f"""
You are a career advisor analyzing a developer's coding profile. Based on the data below, respond ONLY with valid JSON (no markdown, no extra text) matching this exact structure:

{{
  "roles": ["role1", "role2", "role3"],
  "jobs": ["job1", "job2", "job3"],
  "strengths": ["strength1", "strength2", "strength3"],
  "roadmap": ["step1", "step2", "step3"],
  "dos_and_donts": {{"dos": ["do1", "do2"], "donts": ["dont1", "dont2"]}},
  "skill_scores": {{"Problem Solving": 0, "Code Quality": 0, "Data Science": 0, "Consistency": 0}},
  "placement_readiness": {{"score": 0, "reason": "reason_text"}},
  "teacher_tips": ["tip1", "tip2"]
}}

Developer data:
- GitHub: {gh['profile']['public_repos']} public repos, languages used: {gh['languages']}
- LeetCode: {lc_total} problems solved (Easy: {lc_easy}, Medium: {lc_medium}, Hard: {lc_hard}), current streak {lc['streak']['current_streak']} days, max streak {lc['streak']['max_streak']} days
- Kaggle: {kg['notebook_count']} notebooks, {kg['dataset_count']} datasets

Fill skill_scores and placement_readiness score with integers 0-100 based on the data above. Keep each list item short (under 15 words). Respond with ONLY the JSON object, nothing else.
"""
    return prompt


def build_simple_prompt(data):
    gh = data["github"]
    lc = data["leetcode"]
    kg = data["kaggle"]
    lc_total = lc["stats"]["acSubmissionNum"][0]["count"]

    return f"""Respond with ONLY this JSON, filling in the blanks based on: {gh['profile']['public_repos']} GitHub repos, {lc_total} LeetCode problems solved, {kg['notebook_count']} Kaggle notebooks.
{{"roles": ["role1","role2","role3"], "jobs": ["job1","job2"], "strengths": ["s1","s2","s3"], "roadmap": ["r1","r2","r3"], "dos_and_donts": {{"dos": ["d1","d2"], "donts": ["d1","d2"]}}, "skill_scores": {{"Problem Solving": 50, "Code Quality": 50, "Data Science": 50, "Consistency": 50}}, "placement_readiness": {{"score": 50, "reason": "moderate status"}}, "teacher_tips": ["tip1","tip2"]}}"""


def _call_gemini(prompt):
    model = genai.GenerativeModel("gemini-2.5-flash")
    response = model.generate_content(prompt, request_options={"timeout": 20})
    text = response.text.strip()
    text = text.replace("```json", "").replace("```", "").strip()
    return json.loads(text)


def generate_insights(data):
    try:
        return _call_gemini(build_prompt(data))
    except Exception:
        pass

    try:
        return _call_gemini(build_simple_prompt(data))
    except Exception:
        return None