from flask_jwt_extended.utils import get_jwt_identity
from flask_jwt_extended.view_decorators import jwt_required
from flask_restful import Resource
from http import HTTPStatus
from flask import request
from mysql.connector.errors import Error

from utils_MySQL_connection import get_cnx


class ReviewListResource(Resource):
    def get(self, movie_id) : #내가 작성한 리뷰 보기
        try:
            cnx = get_cnx()

            # todo: write SQL
            query = '''select
                    m.title, u.name, u.gender, r.rating, r.content
                    from rating r
                        join movie m
                            on r.movie_id = m.id
                        join user u 
                            on r.user_id = u.id 
                    where m.id = %s;'''

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

        return {'count':len(record_list), 'data': record_list}

    @jwt_required() # 헤더를 통해 토큰을 받음
    def post(self, movie_id) : #리뷰 작성
        data = request.get_json()
        user_id = get_jwt_identity()

        # MySQL
        try:
            cnx = get_cnx()
            
            query = '''insert into rating
                        (user_id, movie_id, rating, content)
                        values
                        (%s, %s, %s, %s);'''
            
            record = (user_id, movie_id, data['rating'], data['content'])
            
            cursor = cnx.cursor()
            cursor.execute(query,record)
            cnx.commit()

        except Error as e:
            print('Error ', e)
            return {'result':'이미 리뷰를 작성 했습니다.', 'error':str(e)}, HTTPStatus.BAD_REQUEST
        finally :
            if cnx.is_connected():
                cursor.close()  # 커서 닫음
                cnx.close()     # 연결 닫음

        # 최종 결과 응답 (성공)
        return {'return': '리뷰를 작성했습니다.'}, HTTPStatus.OK

    @jwt_required() # 헤더를 통해 토큰을 받음
    def delete(self, movie_id): #리뷰 삭제
        try: 
            cnx = get_cnx()
            user_id = get_jwt_identity()    

            query = '''delete
                        from rating
                            where user_id = %s
                            and movie_id = %s;'''

            record = (user_id, movie_id)
            cursor = cnx.cursor()
            cursor.execute(query, record)
            cnx.commit()

        except Error as e:
            print('Error ', e)
            return {'error' : str(e)} , HTTPStatus.BAD_REQUEST
        finally :
            if cnx.is_connected():
                cursor.close()
                cnx.close()
                print('MySQL connection is closed')
        return {'result' : '리뷰가 삭제되었습니다.'}, HTTPStatus.OK

    @jwt_required() # 헤더를 통해 토큰을 받음
    def put(self, movie_id): # 리뷰 수정
        try:
            cnx = get_cnx()
            user_id = get_jwt_identity()
            data = request.get_json()

            query = '''update
                        rating
                        set rating = %s,
                            content = %s
                                where user_id = %s
                                and movie_id = %s;'''
            
            record = (data['rating'], data['content'], user_id, movie_id)
            cursor = cnx.cursor()
            cursor.execute(query, record)
            cnx.commit()

        except Error as e:
            print('Error ', e)
            return {'error' : str(e)} , HTTPStatus.BAD_REQUEST
        finally :
            if cnx.is_connected():
                cursor.close()
                cnx.close()
                print('MySQL connection is closed')
        return {'result' : '리뷰가 수정되었습니다.'}, HTTPStatus.OK





