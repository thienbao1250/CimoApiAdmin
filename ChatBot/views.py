import spacy
import re
import joblib
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime
from rest_framework.parsers import JSONParser
from rest_framework.permissions import AllowAny
from django.conf import settings
import requests
import httpx
from asgiref.sync import async_to_sync

# Load mô hình NER
nlp_ner = spacy.load("model_AI/ner_model")
API_ROUTES = {
    "xin nghỉ": "http://localhost:8000/parents/process-leave-request",
    "xem điểm danh": "http://localhost:8000/students/check_in/",
    "lịch học": "http://localhost:8000/users/check_timetable/",
    # "lịch họp": "/api/meeting-schedule"
}
async def call_api(classified_type, payload):
    api_url = API_ROUTES.get(classified_type)
    # if api_url:
    #     requests.post(api_url, json=payload)
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.post(api_url, json=payload)

        # if response.status_code == 200:
        # print(response.status_code)
        data = response.json()
        return data
        # else:
        #     return response.json()
    except requests.exceptions.RequestException as e:
        print("Lỗi kết nối:", e)
        return None
    
async def call_api_rasa(payload):
    api_url = 'http://localhost:5009/webhooks/rest/webhook'
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.post(api_url, json=payload)
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except requests.exceptions.RequestException as e:
        print("Lỗi kết nối:", e)
        return None
# Định nghĩa lớp APIView
class PredictAPIView(APIView):
    permission_classes = [AllowAny]
    parser_classes = [JSONParser]
    
    def post(self, request):
        sender = request.data.get("sender")
        text = request.data.get("text", "")
        # print(sender)
        if not text:
            return Response({"error": "Vui lòng cung cấp văn bản!"}, status=status.HTTP_400_BAD_REQUEST)

        # Nhận diện tên
        doc = nlp_ner(text)
        names = [ent.text for ent in doc.ents if ent.label_ == "PERSON"]

        # Nhận diện ngày
        # date_pattern = r"\b\d{1,2}/\d{1,2}(?:/\d{4})?\b"
        date_range_pattern = r'(\d{1,2}/\d{1,2}(?:/\d{4})?)\s*(?:đến|đến ngày| tới ngày|) *(\d{1,2}/\d{1,2}(?:/\d{4})?)'
        range_match = re.search(date_range_pattern, text)

        def format_date(date_str):
            # Nếu thiếu năm -> gán năm mặc định hoặc năm hiện tại
            year_now = datetime.now().year
            if date_str.count('/') == 1:
                date_str = f"{date_str}/{year_now}"   # Có thể dùng datetime.now().year nếu muốn
            return datetime.strptime(date_str, "%d/%m/%Y").strftime("%Y-%m-%d")

        if range_match:
            date_start = format_date(range_match.group(1))
            date_end = format_date(range_match.group(2))
        else:
            # Nếu không tìm được khoảng ngày thì fallback về 1 ngày
            single_date_pattern = r'(\d{1,2}/\d{1,2}/\d{4})'
            dates = re.findall(single_date_pattern, text)
            if dates:
                date_start = format_date(dates[0])
                date_end = date_start
            else:
                date_start = None
                date_end = None
        # Nhận diện lý do
        reason_pattern = r"(?:vì|do|tại) (.+)"
        reason_match = re.search(reason_pattern, text)
        reason = reason_match.group(1) if reason_match else "Không xác định"

        # Phân loại câu (Nếu bạn có model đã train)
        try:
            vectorizer = joblib.load("model_AI/vectorizer.pkl")
            classifier = joblib.load("model_AI/classifier.pkl")
            X_input = vectorizer.transform([text])
            predicted_category = classifier.predict(X_input)[0]
        except:
            predicted_category = False
        # for i in names:
        print(predicted_category)
        # print(names)
        payload =({
            "sender_id":sender,
            "student_name": names if names else False,
            "start_date": date_start  if date_start else False,
            "end_date": date_end  if date_end  else False,
            "reason": reason
            # "Thể loại câu": predicted_category
        })
        print("Ngày bắt đầu:", date_start)
        print("Ngày kết thúc:", date_end)
        print(payload["student_name"])
        response_data = None
        # print(predicted_category)
        if not payload["student_name"] == False and predicted_category:
            response_data = async_to_sync(call_api)(predicted_category, payload)

        if response_data == None or predicted_category == False:
            # api_url = 'http://localhost:5009/webhooks/rest/webhook'
            payloadd=({
                "sender":sender,
                "message": text
            })
            response_data_bot = async_to_sync(call_api_rasa)(payloadd)
            return Response(response_data_bot,status=200)
            
        return Response(response_data,status=200)
        #     "Tên": names if names else "Không xác định",
        #     "Ngày": dates[0] if dates else "Không xác định",
        #     "Lý do": reason,
        #     "Thể loại câu": predicted_category
        # })
#pip install django djangorestframework spacy joblib scikit-learn
