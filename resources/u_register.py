from flask_restful import Resource
from http import HTTPStatus
from flask import request

from utils_MySQL_connection import get_cnx

from mysql.connector.errors import Error
from email_validator import validate_email, EmailNotValidError
from flask_jwt_extended import create_access_token
from utils_p2h import hash_password


class UserRegisterResource(Resource):
    def post(self) :
        data = request.get_json()

        # 이메일 검사
        try:
            valid = validate_email(data['email'])
            # 통과
        except EmailNotValidError as e:
            print(f'이메일 형식 에러 \n{str(e)}') #이메일 형식 에러/터미널
            return {'email_error':'이메일 주소가 잘못되었습니다.'}, HTTPStatus.BAD_REQUEST #이메일 형식 에러/응답

        # 비밀번호 조건 확인
        # 여기서는 10~16자리의 문자열로 지정 (형식 무관)
        pw_length = len (data['password'])
        if pw_length < 10 or pw_length > 17:
            return {'error':'비밀번호의 길이가 맞지 않습니다.'}, HTTPStatus.BAD_REQUEST #비밀번호 길이 에러/응답
        del pw_length

        # 비밀번호 암호화 (해시)
        hashed_pw = hash_password(data['password'])

        # MySQL
        try:
            cnx = get_cnx()
            
            query = '''insert into user
                    (email, password, name, gender)
                    values
                    (%s, %s, %s, %s);'''
            
            record = (
                data['email'],
                hashed_pw,
                data['name'],
                data['gender'])
            
            cursor = cnx.cursor()
            cursor.execute(query,record)
            cnx.commit()
            user_id = cursor.lastrowid #DB 내 users 테이블의 id

        except Error as e:
            print('Error ', e) # 회원 가입 에러/터미널
            return {'result':'이미 가입된 회원입니다.', 'error':str(e)}, HTTPStatus.BAD_REQUEST # 회원 가입 에러/응답
        finally :
            if cnx.is_connected():
                cursor.close()  # 커서 닫음
                cnx.close()     # 연결 닫음

        # JWT 토큰 발행
        access_token = create_access_token(user_id)

        # 최종 결과 응답 (성공)
        return {'return': '회원가입에 성공했습니다.',
                'access_token':access_token}, HTTPStatus.OK
