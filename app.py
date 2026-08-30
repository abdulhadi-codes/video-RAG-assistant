import os
from flask import Flask, request, jsonify, render_template
from rag_pipeline import answer_question, df

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/health")
def health():
    return jsonify({"status": "ok", "chunks_loaded": len(df)})


@app.route("/query", methods=["POST"])
def query():
    data = request.get_json(force=True)
    question = (data or {}).get("question", "").strip()

    if not question:
        return jsonify({"error": "question is required"}), 400

    try:
        result = answer_question(question)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)