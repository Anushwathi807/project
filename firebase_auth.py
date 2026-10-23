import firebase_admin
from firebase_admin import credentials, auth

cred = credentials.Certificate("firebase-service-account.json")
firebase_admin.initialize_app(cred)

def verify_token(id_token):
    try:
        decoded_token = auth.verify_id_token(id_token)
        return decoded_token
    except Exception as e:
        return None
from firebase_admin import firestore

db = firestore.client()

def save_report(uid, report_data):
    doc_ref = db.collection("reports").document()
    doc_ref.set({
        "uid": uid,
        "created_at": firestore.SERVER_TIMESTAMP,
        "data": report_data
    })
    return doc_ref.id

def get_user_reports(uid):
    reports_ref = db.collection("reports").where("uid", "==", uid).order_by("created_at", direction=firestore.Query.DESCENDING)
    docs = reports_ref.stream()

    reports = []
    for doc in docs:
        report = doc.to_dict()
        report["id"] = doc.id
        if report.get("created_at"):
            report["created_at"] = report["created_at"].isoformat()
        reports.append(report)

    return reports