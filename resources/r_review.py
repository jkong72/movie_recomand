from flask_jwt_extended.utils import get_jwt_identity
from flask_restful import Resource
from http import HTTPStatus
from flask import request

from utils_MySQL_connection import get_cnx

from mysql.connector.errors import Error
from email_validator import validate_email, EmailNotValidError
from flask_jwt_extended.view_decorators import jwt_required
from flask_jwt_extended import create_access_token
from utils_p2h import hash_password


class ReviewCreateResource(Resource):
    def get(self, movie_id) :
        try:
            cnx = get_cnx()


            # todo: write SQL
            query = '''select *
            from rating
            where id = %s'''

            param = (movie_id,)
            cursor = cnx.cursor(dictionary = True)
            cursor.execute(query, param)
            record_list = cursor.fetchall()

        except Error as e:
            print('Error ', e)
            return {'result':'에러가 발생했습니다.', 'error':str(e)}, HTTPStatus.BAD_REQUEST
        finally :
            if cnx.is_connected():
                cursor.close()  # 커서 닫음
                cnx.close()     # 연결 닫음

        return()

    @jwt_required() # 헤더를 통해 토큰을 받음
    def post(self, movie_id) :
        data = request.get_json()
        user_id = get_jwt_identity()

        # MySQL
        try:
            cnx = get_cnx()
            
            query = '''insert into rating
                        (user_id, movie_id, rating)
                        values
                        (%s, %s, %s);'''
            
            record = (user_id, movie_id, data['rating'])
            
            cursor = cnx.cursor()
            cursor.execute(query,record)
            cnx.commit()

        except Error as e:
            print('Error ', e)
            return {'result':'에러가 발생했습니다.', 'error':str(e)}, HTTPStatus.BAD_REQUEST
        finally :
            if cnx.is_connected():
                cursor.close()  # 커서 닫음
                cnx.close()     # 연결 닫음

        # 최종 결과 응답 (성공)
        return {'return': '리뷰를 작성했습니다.'}, HTTPStatus.OK
