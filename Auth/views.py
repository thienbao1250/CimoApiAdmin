from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime, timedelta
from Parents.models import SoParents
from Parents.serializers import SoParentsSerializer
import jwt
from django.conf import settings
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError

def create_jwt_token(payload: dict, expires_in_seconds: int = 86400):
    payload_copy = payload.copy()
    payload_copy["exp"] = datetime.utcnow() + timedelta(seconds=expires_in_seconds)
    token = jwt.encode(payload_copy, settings.SECRET_KEY, algorithm="HS256")
    return token

def decode_jwt_token(token: str):
    try:
        decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        
        # Kiểm tra thời gian hết hạn thủ công (1 ngày tính từ thời điểm phát hành)
        if "exp" in decoded:
            exp_time = datetime.fromtimestamp(decoded["exp"])
            now = datetime.utcnow()

            if now > exp_time:
                return {"valid": False, "error": "Token quá hạn cho phép"}
            
            # if (exp_time - now) > timedelta(seconds=1):
            #     return {"valid": True, "payload": decoded}
                
            return {"valid": True, "payload": decoded}
        

    except ExpiredSignatureError as e:
        return {"valid": False, "error": str(e)}
    except InvalidTokenError:
        return {"valid": False, "error": "Token không hợp lệ"}
def veriry_token(auth_header):
    if not auth_header or not auth_header.startswith('Bearer '):
        return {"valid": False, "error": "Thiếu hoặc sai định dạng Authorization header"}

    token = auth_header.split('Bearer ')[1]
    result = decode_jwt_token(token)
    return result  # Luôn là dict {valid, error?, payload?}

class VerifyOtpAPI(APIView):
    def post(self, request):
        phone = request.data.get('phone')
        otp = request.data.get('otp')
        parent = SoParents.objects.filter(phone=phone).first()
        if parent is None:
            return Response({'message': 'Tài khoản không tồn tại'}, status=400)
        if otp != "123456":
            return Response({'message': 'Mã OTP không đúng'}, status=400)

        serializer = SoParentsSerializer(parent)
        data = {
            'parent': serializer.data['id'],

        }

        token = create_jwt_token(data)
        decode = decode_jwt_token(token)
        return Response({'message': 'Xác thực thành công', 'token': token, "decode":decode}, status=200)

# Create your views here.
class Login_Parents(APIView):
    def post(self, request):
        
        # Xử lý logic tạo token ở đây
        # Ví dụ: tạo token ngẫu nhiên hoặc sử dụng thư viện như PyJWT
        # Trả về token trong phản hồi
        return Response({"token": "your_token_here"})
    
