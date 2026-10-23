from github_module import get_github_summary
from leetcode_module import get_leetcode_summary
from kaggle_module import get_kaggle_summary

def get_full_summary(github_input, leetcode_input, kaggle_input):
    return {
        "github": get_github_summary(github_input),
        "leetcode": get_leetcode_summary(leetcode_input),
        "kaggle": get_kaggle_summary(kaggle_input)
    }