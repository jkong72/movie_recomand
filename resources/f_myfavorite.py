from flask_restful import Resource
from flask import request
from http import HTTPStatus
from mysql.connector.errors import Error
from flask_jwt_extended import jwt_required, get_jwt_identity

from utils_MySQL_connection import get_cnx


class FavoriteListResource(Resource):
    @jwt_required(optional=False)
    def get(self):
        parameter_dict = request.args.to_dict()
        try :
            # 1. DB 에 연결
            cnx = get_cnx()        
            user_id = get_jwt_identity()
            
            offset = int(parameter_dict['offset'])
            limit = int(parameter_dict['limit'])
            
            try:
                if offset >1 :
                    page = (offset-1)*25
                elif offset==0:
                    page = 0
            except UnboundLocalError as e:
                return {'result':'페이지 수가 잘못되었습니다.', 'error':str(e)},HTTPStatus.BAD_REQUEST

            # 2. 쿼리문 만들고
            query = '''select m.id, m.title, m.genre
                        from favorite f
                            join movie m
                                on f.movie_id = m.id
                        where user_id = %s
                        limit %s, %s;'''

            param = (user_id, offset, limit)
            cursor = cnx.cursor(dictionary = True)
            cursor.execute(query, param)
            record_list = cursor.fetchall()
        

        except Error as e:
            print('Error ', e)
            return {'error' : str(e)} , HTTPStatus.BAD_REQUEST
        finally :
            if cnx.is_connected():
                cursor.close()
                cnx.close()
                print('MySQL connection is closed')

        return {'count':len(record_list), 'data' : record_list},HTTPStatus.OK
