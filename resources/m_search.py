from flask_restful import Resource
from flask import request
from http import HTTPStatus
from mysql.connector.errors import Error

from utils_MySQL_connection import get_cnx


class MovieSearchResource(Resource):
    def get (self):
        parameter_dict = request.args.to_dict()
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
            
       
            
            query = '''select
                    m.title,
                    count(r.id) as review_count,
                    ifnull(avg(r.rating),0) as rating_avg
                    from movie m
                    left join rating r
                        on m.id = r.movie_id
                    where m.title like %s
                    limit %s, %s;'''

            keyword = '%' + parameter_dict['keyword']+ '%'
            param = (keyword, page, limit)
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


