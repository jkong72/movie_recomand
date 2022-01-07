from flask_restful import Resource
from flask import request
from http import HTTPStatus
from mysql.connector.errors import Error

from utils_MySQL_connection import get_cnx


class MovieListResource(Resource):
    def get(self):
        parameter_dict = request.args.to_dict()
        # var = request.args.to_dict(param)
        # 위 코드로 하나의 파라미터만 가져와 변수에 저장할 수 있음.
        print (parameter_dict)
        try :
            cnx = get_cnx()
            # n은 (페이지-1)*25

            offset = int(parameter_dict['offset'])
            limit = int(parameter_dict['limit'])
            
            try:
                if offset >1 :
                    page = (offset-1)*25
                elif offset==0:
                    page = 0
            except UnboundLocalError as e:
                return {'result':'페이지 수가 잘못되었습니다.', 'error':str(e)},HTTPStatus.BAD_REQUEST
            
            try:
                if parameter_dict['order'] == 'stars':
                    order = 'rating_avg'
                elif parameter_dict['order'] == 'count':
                    order = 'review_count'
            except UnboundLocalError as e:
                return {'result':'정렬 기준이 잘못되었습니다.', 'error':str(e)},HTTPStatus.BAD_REQUEST    
        
            
            query = '''select
                    m.title,
                    count(r.id) as review_count,
                    avg(r.rating) as rating_avg
                    from movie m
                    join rating r
                        on r.movie_id = m.id
                    group by m.id
                    order by %s desc
                    limit %s, %s;'''

            param = (order, page, limit)
            cursor = cnx.cursor(dictionary = True)
            cursor.execute(query, param)
            record_list = cursor.fetchall()

            i = 0
            for record in record_list :
                record_list[i]['rating_avg'] = float(record_list[i]['rating_avg'])
                i = i+1

        except Error as e:
            print('Error while connecting to MySQL\n',e)
            return {'error':str(e)}, HTTPStatus.BAD_REQUEST

        finally :
            cursor.close()
            if cnx.is_connected():
                cnx.close()
                print('MySQL connection is closed')
            else:
                print('connection does not exist')

                
        return {'count':len(record_list), 'movie_list':record_list}, HTTPStatus.OK



