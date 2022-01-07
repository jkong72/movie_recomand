# 학습용 데이터
# 수정 전의 코드. 비교를 위해 남겨져 있는 것으로 실제 서비스에 사용되지 않음

from flask_jwt_extended.utils import get_jwt_identity
from flask_jwt_extended.view_decorators import jwt_required
from flask_restful import Resource
from http import HTTPStatus

from mysql.connector.errors import Error
from utils_MySQL_connection import get_cnx

class UserInformationResource(Resource):
    @jwt_required() # 헤더를 통해 토큰을 받음
    def get (self):
        user_id = get_jwt_identity()
        try:
            cnx = get_cnx()
            # 유저의 정보 가져오기
            query = '''select * from user
                    where id = %s;'''

            param = (user_id,)
            cursor = cnx.cursor(dictionary = True)
            cursor.execute(query, param)
            record_list = cursor.fetchall()

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

            response = {'email':record_list[0]['email'],
                        'name':record_list[0]['name'],
                        'gender':record_list[0]['gender']}
            
            try:
                cnx = get_cnx()
                # 유저의 정보 가져오기
                query = '''select * from rating
                        where user_id = %s;'''

                param = (user_id,)
                cursor = cnx.cursor(dictionary = True)
                cursor.execute(query, param)
                record_list = cursor.fetchall()

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


                #todo: 리뷰 표시 형식 참고
                # 리뷰가 없으면 없다고 응답
                reviews = record_list

                # 반환받은 정보를 클라이언트에 응답.
                # if record_list 
                return {'data':response, 'reviews':record_list}, HTTPStatus.OK