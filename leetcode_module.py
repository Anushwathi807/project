import requests
import datetime
import json


def extract_leetcode_username(user_input):
    user_input = user_input.strip()
    if "leetcode.com" in user_input:
        parts = user_input.rstrip('/').split('/')
        return parts[-1]
    return user_input


def get_leetcode_stats(username):
    url = "https://leetcode.com/graphql"
    query = """
    query getUserStats($username: String!) {
        matchedUser(username: $username) {
            submitStats {
                acSubmissionNum {
                    difficulty
                    count
                }
                totalSubmissionNum {
                    difficulty
                    count
                }
            }
        }
    }
    """
    variables = {"username": username}

    try:
        response = requests.post(url, json={"query": query, "variables": variables}, timeout=10)
    except requests.exceptions.RequestException:
        return None

    if response.status_code != 200:
        return None

    data = response.json()
    matched_user = data.get("data", {}).get("matchedUser")

    if matched_user is None:
        return None

    return matched_user["submitStats"]


def get_leetcode_streak(username):
    url = "https://leetcode.com/graphql"
    query = """
    query getUserCalendar($username: String!) {
        matchedUser(username: $username) {
            userCalendar {
                submissionCalendar
            }
        }
    }
    """
    variables = {"username": username}

    try:
        response = requests.post(url, json={"query": query, "variables": variables}, timeout=10)
    except requests.exceptions.RequestException:
        return {"current_streak": 0, "max_streak": 0}

    if response.status_code != 200:
        return {"current_streak": 0, "max_streak": 0}

    data = response.json()
    matched_user = data.get("data", {}).get("matchedUser")

    if matched_user is None:
        return {"current_streak": 0, "max_streak": 0}

    calendar_raw = matched_user["userCalendar"]["submissionCalendar"]
    calendar = json.loads(calendar_raw)

    active_days = sorted(int(ts) for ts in calendar.keys())
    active_dates = set(
        datetime.datetime.utcfromtimestamp(ts).date() for ts in active_days
    )

    return calculate_streaks(active_dates)


def calculate_streaks(active_dates):
    if not active_dates:
        return {"current_streak": 0, "max_streak": 0}

    sorted_dates = sorted(active_dates)
    max_streak = 1
    current_run = 1

    for i in range(1, len(sorted_dates)):
        if (sorted_dates[i] - sorted_dates[i - 1]).days == 1:
            current_run += 1
            max_streak = max(max_streak, current_run)
        else:
            current_run = 1

    today = datetime.date.today()
    if today in sorted_dates or (today - datetime.timedelta(days=1)) in sorted_dates:
        current_streak = 1
        for i in range(len(sorted_dates) - 1, 0, -1):
            if (sorted_dates[i] - sorted_dates[i - 1]).days == 1:
                current_streak += 1
            else:
                break
    else:
        current_streak = 0

    return {"current_streak": current_streak, "max_streak": max_streak}


def get_leetcode_solved_problems(username, limit=50):
    url = "https://leetcode.com/graphql"
    query = """
    query getSolvedProblems($username: String!, $limit: Int!) {
        recentAcSubmissionList(username: $username, limit: $limit) {
            title
            titleSlug
            timestamp
        }
    }
    """
    variables = {"username": username, "limit": limit}

    try:
        response = requests.post(url, json={"query": query, "variables": variables}, timeout=10)
    except requests.exceptions.RequestException:
        return []

    if response.status_code != 200:
        return []

    data = response.json()
    submissions = data.get("data", {}).get("recentAcSubmissionList")

    if submissions is None:
        return []

    return submissions


def get_leetcode_languages(username):
    url = "https://leetcode.com/graphql"
    query = """
    query getLanguageStats($username: String!) {
        matchedUser(username: $username) {
            languageProblemCount {
                languageName
                problemsSolved
            }
        }
    }
    """
    variables = {"username": username}

    try:
        response = requests.post(url, json={"query": query, "variables": variables}, timeout=10)
    except requests.exceptions.RequestException:
        return []

    if response.status_code != 200:
        return []

    data = response.json()
    matched_user = data.get("data", {}).get("matchedUser")

    if matched_user is None:
        return []

    return matched_user["languageProblemCount"]


def get_problem_topics(title_slug):
    url = "https://leetcode.com/graphql"
    query = """
    query getProblemTopics($titleSlug: String!) {
        question(titleSlug: $titleSlug) {
            topicTags {
                name
            }
        }
    }
    """
    variables = {"titleSlug": title_slug}

    try:
        response = requests.post(url, json={"query": query, "variables": variables}, timeout=10)
    except requests.exceptions.RequestException:
        return []

    if response.status_code != 200:
        return []

    data = response.json()
    question = data.get("data", {}).get("question")

    if question is None:
        return []

    return [tag["name"] for tag in question["topicTags"]]


def attach_topics_to_problems(problems, limit=5):
    for problem in problems[:limit]:
        problem["topics"] = get_problem_topics(problem["titleSlug"])
    for problem in problems[limit:]:
        problem["topics"] = []
    return problems


def get_leetcode_summary(user_input):
    username = extract_leetcode_username(user_input)
    stats = get_leetcode_stats(username)

    if stats is None:
        return {"error": f"LeetCode user '{username}' not found"}

    streak = get_leetcode_streak(username)
    recent_solved = get_leetcode_solved_problems(username)
    recent_solved = attach_topics_to_problems(recent_solved)
    languages = get_leetcode_languages(username)

    return {
        "username": username,
        "stats": stats,
        "streak": streak,
        "recent_solved_problems": recent_solved,
        "languages": languages
    }