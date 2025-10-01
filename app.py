from flask import Flask, request, jsonify
import requests, os
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

@app.route('/')
def home():
    return "✅ KCSC 필터링 서버 정상 작동"

@app.route('/kcsc_filter', methods=['GET'])
def kcsc_filter():
    try:
        kcsc_api_key = os.getenv("KCSC_API_KEY")
        query = request.args.get("query", "")

        # 1. KCSC API 호출
        kcsc_url = f"https://kcsc.re.kr/OpenApi/CodeList?key={kcsc_api_key}"
        resp = requests.get(kcsc_url)
        if resp.status_code != 200:
            return jsonify({"error": "KCSC API 호출 실패"}), 500

        # 2. JSON 파싱
        kcsc_data = resp.json()   # ← text가 아니라 json으로 파싱
        items = kcsc_data if isinstance(kcsc_data, list) else kcsc_data.get("list", [])

        # 3. 검색 & 필터링
        if query:
            filtered = [item for item in items if query in str(item)]
        else:
            filtered = items[:200]  # 기본적으로 앞부분 일부만 제공

        # 4. 구조화 (간단히 index + 내용)
        structured = [
            {"index": i, "code": item.get("code"), "name": item.get("name")}
            for i, item in enumerate(filtered)
        ]

        return jsonify({
            "query": query,
            "count": len(structured),
            "results": structured
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/kcsc_filter_raw', methods=['GET'])
def kcsc_filter_raw():
    """KCSC API 원본 응답 그대로 보기"""
    try:
        kcsc_api_key = os.getenv("KCSC_API_KEY")
        kcsc_url = f"https://kcsc.re.kr/OpenApi/CodeList?key={kcsc_api_key}"
        resp = requests.get(kcsc_url)
        return resp.json(), resp.status_code
    except Exception as e:
        return str(e), 500


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

