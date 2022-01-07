from flask_restful import Resource
from http import HTTPStatus
from mysql.connector.errors import Error
from flask_jwt_extended import jwt_required, get_jwt_identity

from utils_MySQL_connection import get_cnx


class FavoriteSwitchResource(Resource) :
    @jwt_required(optional=False)
    def post(self, movie_id) :

        try :
            # 1. DB 에 연결
            cnx = get_cnx()        
            user_id = get_jwt_identity()
            
            # 2. 쿼리문 만들고
            query = '''insert
                        into favorite
                            (user_id, movie_id)
                        value (%s, %s);'''

            record = (user_id , movie_id)
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

        return {'result' : '즐겨찾기에 추가 되었습니다.'},HTTPStatus.OK


    @jwt_required(optional=False)
    def delete(self, movie_id) :
        try :
            # 1. DB 에 연결
            cnx = get_cnx()            
            user_id = get_jwt_identity()

            # 2. 쿼리문 만들고
            query = '''delete
                    from favorite
                        where user_id = %s
                        and movie_id = %s ;'''
            # 파이썬에서, 튜플만들때, 데이터가 1개인 경우에는 콤마를 꼭
            # 써준다.
            record = (user_id , movie_id)
            
            # 3. 커넥션으로부터 커서를 가져온다.
            cursor = cnx.cursor()

            # 4. 쿼리문을 커서에 넣어서 실행한다.
            cursor.execute(query, record)

            # 5. 커넥션을 커밋한다.=> 디비에 영구적으로 반영하라는 뜻.
            cnx.commit()

        except Error as e:
            print('Error ', e)
            return {'error' : str(e)} , HTTPStatus.BAD_REQUEST
        finally :
            if cnx.is_connected():
                cursor.close()
                cnx.close()
                print('MySQL connection is closed')
                
        return {'result' : '즐겨찾기에서 삭제되었습니다.'},HTTPStatus.OK