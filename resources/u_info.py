from flask_jwt_extended.utils import get_jwt_identity
from flask_jwt_extended.view_decorators import jwt_required
from flask_restful import Resource
from flask import request
from http import HTTPStatus
from mysql.connector.errors import Error

from utils_MySQL_connection import get_cnx


class UserInformationResource(Resource):
    @jwt_required() # 헤더를 통해 토큰을 받음
    def get (self):
        user_id = get_jwt_identity()
        parameter_dict = request.args.to_dict()
        try:
            cnx = get_cnx()
            # 유저의 정보 가져오기

            offset = int(parameter_dict['offset'])
            limit = int(parameter_dict['limit'])
            
            try:
                if offset >1 :
                    page = (offset-1)*25
                elif offset==0:
                    page = 0
            except UnboundLocalError as e:
                return {'result':'페이지 수가 잘못되었습니다.', 'error':str(e)},HTTPStatus.BAD_REQUEST

            query = '''select id, email, name, gender
                    from user
                    where id = %s;'''

            param = (user_id,)
            cursor = cnx.cursor(dictionary = True)
            cursor.execute(query, param)
            record_list = cursor.fetchall()

            # i = 0
            # for record in record_list:
            #     record_list[i]['created_at'] = record['created_at'].isoformat()
            #     i=i+1

            user_info = record_list[0]

            query = '''select r.id, m.title, r.rating
                    from rating r
                    join movie m
                    on r.user_id = %s and r.movie_id = m.id
                    limit %s, %s;'''
            
            param = (user_id, offset, limit)

            cursor = cnx.cursor(dictionary = True)
            cursor.execute(query, param)
            record_list = cursor.fetchall()
            
            review_list = record_list


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
            
        return {'data':user_info, 'count':len(review_list), 'reviews':review_list}, HTTPStatus.OK