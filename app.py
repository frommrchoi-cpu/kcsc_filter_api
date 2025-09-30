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
        query = request.args.get("query", "")  # 검색 키워드 (예: '지반')
        
        # 1. KCSC API 호출
        kcsc_url = f"https://kcsc.re.kr/OpenApi/CodeList?key={kcsc_api_key}"
        resp = requests.get(kcsc_url)
        if resp.status_code != 200:
            return jsonify({"error": "KCSC API 호출 실패"}), 500

        # 2. 원본 데이터 → 라인 단위 분할
        raw_data = resp.text.split("\n")

        # 3. 검색 & 필터링
        if query:
            filtered = [line for line in raw_data if query in line]
        else:
            filtered = raw_data[:200]  # 기본적으로 앞부분만 일부 제공

        # 4. 구조화 (JSON 반환)
        structured = [{"index": i, "content": line} for i, line in enumerate(filtered)]

        return jsonify({
            "query": query,
            "count": len(structured),
            "results": structured
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
