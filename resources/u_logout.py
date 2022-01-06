from flask_restful import Resource
from flask_jwt_extended.view_decorators import jwt_required
from flask_jwt_extended import get_jwt

jwt_blacklist = set()

class LogoutResource(Resource) :
    @jwt_required() # 헤더를 통해 토큰을 받음
    def post(self):
        jti = get_jwt()['jti'] # jwt의 고유 id값을 가져옴
        print (jti)

        # 로그아웃한 토큰의 id값을 블랙리스트에 저장
        jwt_blacklist.add(jti)

        # 클라이언트에게 작업 결과 보고
        return {'result':'로그아웃 되었습니다.'}