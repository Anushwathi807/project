import time
from leetcode_module import get_leetcode_summary

start = time.time()
result = get_leetcode_summary("elsysayla")
print("Total time:", time.time() - start, "seconds")
print()

for p in result["recent_solved_problems"][:6]:
    print(p["title"], "->", p["topics"])