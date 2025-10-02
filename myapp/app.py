from flask import Flask, render_template, jsonify
from predictor import Predictor
import requests, re, time

app = Flask(__name__)
predictor = Predictor("model_state.json")

API_URL = (
    "https://draw.ar-lottery01.com/WinGo/WinGo_1M/GetHistoryIssuePage.json"
    "?pageSize=10&pageNo=1&ts={}"
)
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Referer": "https://hgnice.biz",
}


def fetch_results(limit=10):
    ts = int(time.time() * 1000)
    try:
        r = requests.get(API_URL.format(ts), headers=HEADERS, timeout=10)
        r.raise_for_status()
        data = r.json()
        data_list = data.get("data", {}).get("list", []) if isinstance(data, dict) else []
        if not isinstance(data_list, list):
            return []

        entries = []
        for x in data_list:
            if not isinstance(x, dict):
                continue

            issue_val = (
                x.get("issueNumber")
                or x.get("issue")
                or x.get("issueNo")
                or x.get("issue_id")
                or x.get("id")
            )

            num = None
            for key in (
                "number",
                "num",
                "openCode",
                "open_code",
                "result",
                "openResult",
                "openNumber",
                "value",
            ):
                if key in x and x[key] is not None:
                    val = x[key]
                    if isinstance(val, (int, float)):
                        num = int(val) % 10
                        break
                    if isinstance(val, str):
                        groups = re.findall(r"\d+", val)
                        if groups:
                            num = int(groups[-1][-1])
                            break

            if issue_val is None or num is None:
                continue

            try:
                issue_str = str(issue_val)
                issue_digits = re.findall(r"\d+", issue_str)
                if not issue_digits:
                    continue
                issue_int = int(issue_digits[0])
            except Exception:
                continue

            entries.append((issue_int, int(num)))

        entries.sort(key=lambda t: t[0])
        return [(str(i), n) for (i, n) in entries[-limit:]]
    except Exception as e:
        print(f"[ERROR] fetch_results: {e}")
        return []


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/fetch")
def fetch_and_predict():
    results = fetch_results(limit=10)
    if results:
        for _, num in results:
            predictor.add_result(num)

    prediction = predictor.predict_next()

    return jsonify({
        "history": predictor.history[-50:],
        "prediction": prediction
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
