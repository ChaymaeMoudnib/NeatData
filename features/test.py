from flask import Flask, request, jsonify, Blueprint, render_template
from flask_cors import CORS
from pymongo import MongoClient
import os
from werkzeug.utils import secure_filename

# Create Blueprint
db_bp = Blueprint("db", __name__)

# MongoDB connection
client = MongoClient("mongodb://localhost:27017/")
db = client["upload_db"]
collection = db["uploads"]

# File Upload Config
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def test(file, username):
    """Handles file upload and stores information in MongoDB."""
    if file.filename == "":
        return {"message": "No selected file", "status": "error"}, 400

    # Secure filename and save file
    filename = secure_filename(file.filename)
    filepath = os.path.join(UPLOAD_FOLDER, filename)  # ✅ FIXED
    file.save(filepath)

    # Store in MongoDB
    upload_record = {
        "username": username,
        "filename": filename,
        "filepath": filepath,
        "status": "in_progress"
    }
    collection.insert_one(upload_record)

    return {"message": "File uploaded successfully", "filename": filename}, 200

@db_bp.route("/finalize", methods=["POST"])
def finalize_upload():
    """Finalizes data processing after upload."""
    data = request.json
    username = data.get("username")

    if not username:
        return jsonify({"message": "Username required"}), 400

    # Simulate data processing (Replace with real logic)
    processed_result = {"message": "Processing complete", "summary": "User data processed"}

    # Update MongoDB record
    result = collection.update_one(
        {"username": username, "status": "in_progress"},
        {"$set": {"status": "completed", "result": processed_result}}
    )

    if result.matched_count == 0:
        return jsonify({"message": "No record found for user"}), 404

    return jsonify({"message": "Data processing completed"})

@db_bp.route("/results/<username>", methods=["GET"])
def get_results(username):
    """Retrieves processed results for a given username."""
    record = collection.find_one({"username": username})

    if not record:
        return jsonify({"message": "No record found"}), 404

    return jsonify(record)
