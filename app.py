from flask import Flask, render_template, request, jsonify
from firebase_auth import verify_token, save_report, get_user_reports
from aggregator import get_full_summary
from insights_module import generate_insights

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/profiles')
def profiles():
    return render_template('profiles.html')

@app.route('/verify-login', methods=['POST'])
def verify_login():
    data = request.get_json()
    token = data.get('token')
    decoded = verify_token(token)

    if decoded is None:
        return jsonify({"success": False, "message": "Invalid token"}), 401

    return jsonify({"success": True, "email": decoded.get("email"), "uid": decoded.get("uid")})

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.get_json()
    github_input = data.get('github')
    leetcode_input = data.get('leetcode')
    kaggle_input = data.get('kaggle')
    id_token = data.get('token')

    result = get_full_summary(github_input, leetcode_input, kaggle_input)

    if not result["github"].get("error") and not result["leetcode"].get("error"):
        result["insights"] = generate_insights(result)
    else:
        result["insights"] = None

    decoded = verify_token(id_token)
    if decoded is not None:
        uid = decoded.get('uid')
        save_report(uid, result)

    return jsonify(result)

@app.route('/history', methods=['POST'])
def history():
    data = request.get_json()
    id_token = data.get('token')
    decoded = verify_token(id_token)

    if decoded is None:
        return jsonify({"error": "Invalid token"}), 401

    uid = decoded.get('uid')
    reports = get_user_reports(uid)
    return jsonify(reports)

if __name__ == '__main__':
    app.run(debug=True)