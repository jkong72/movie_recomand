from flask_restful import Resource
from http import HTTPStatus
from flask import request
from mysql.connector.errors import Error
from flask_jwt_extended import create_access_token
from utils_p2h import check_password

from utils_MySQL_connection import get_cnx


class UserLoginResource(Resource):
    def post(self):
        data = request.get_json()
        try:
            cnx = get_cnx() #DB와 연결

            # MySQL(쿼리문)
            query = '''select *
                    from user
                    where email = %s;'''

            param = (data['email'], ) #변수 지정
            cursor = cnx.cursor(dictionary = True)
            cursor.execute(query, param) #커서를 통해 실행
            record_list = cursor.fetchall() #가져온 데이터 저장

            # 요청에는 항상 JSON 형식을 통해 응답해야 하며
            # 시간 형식이 JSON 파일과 맞지 않으므로 문자열로 바꾸어주었다.
            i = 0
            for record in record_list:
                record_list[i]['created_at'] = record['created_at'].isoformat()
                i=i+1

        except Error as e:
            print('Error while connecting to MySQL\n',e) #DB 통신 에러/터미널
            return {'error':str(e)}, HTTPStatus.BAD_REQUEST #DB 통신 에러/응답
        
        finally :
            cursor.close()
            if cnx.is_connected():
                cnx.close()
                print('MySQL connection is closed')
            else:
                print('connection does not exist')


        if len (record_list) == 0: 
            return {'error': '가입된 이메일이 없습니다.'}, HTTPStatus.BAD_REQUEST #없는 이메일 에러/응답
        
        if  check_password(data['password'], record_list[0]['password']) == False: #비밀번호 에러/터미널
            return {'error': '비밀번호가 일치하지 않습니다.'}, HTTPStatus.UNAUTHORIZED #비밀번호 에러/응답

        # 로그인에 성공했다면 JWT를 발행 및 반환
        user_id = record_list[0]['id']
        access_token =create_access_token(user_id)
        return {'reult':'로그인 성공', 'access_token':access_token}