from flask_restful import Resource
from http import HTTPStatus
from mysql.connector.errors import Error

from utils_MySQL_connection import get_cnx


class MovieDetailResource(Resource):
    def get(self, movie_id):
        try :
            cnx = get_cnx()        
            
            query = '''select
                    m.id,
                    m.title,
                    m.attendance,
                    m.year,
                    ifnull (avg(r.rating), 0) as rating_avg
                    from movie m

                    join rating r
                        on r.movie_id = m.id
                    where m.id = %s
                    group by m.id;'''

            param = (movie_id, )
            cursor = cnx.cursor(dictionary = True)
            cursor.execute(query, param)
            record_list = cursor.fetchall()
            print (record_list)

            i = 0
            for record in record_list :
                record_list[i]['rating_avg'] = float(record_list[i]['rating_avg'])
                record_list[i]['year'] = str(record_list[i]['year'])
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

                
        return {'movie_list':record_list}, HTTPStatus.OK




