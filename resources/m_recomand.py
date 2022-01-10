from flask_jwt_extended.utils import get_jwt_identity
from flask_jwt_extended.view_decorators import jwt_required
from flask_restful import Resource
from http import HTTPStatus
from mysql.connector.errors import Error
import pandas as pd

from utils_MySQL_connection import get_cnx


class MovieRecommandResource(Resource):
    @jwt_required() # 헤더를 통해 토큰을 받음
    def get (self):
        user_id = get_jwt_identity()
        try:
            cnx = get_cnx()
            
            query = '''select
                        r.id,
                        r.user_id,
                        r.movie_id,
                        r.rating,
                        m.title
                    from rating r
                    join movie m
                        on r.user_id = %s
                        and r.movie_id = m.id;'''

            param = (user_id,)
            cursor = cnx.cursor(dictionary = True)
            cursor.execute(query, param)
            record_list = cursor.fetchall()

            record_list = pd.DataFrame(record_list)
            recom_movie = pd.read_csv('data/movies_corr.csv', index_col=['title'])

            similar_movies_list = pd.DataFrame()
            for i in range(record_list.shape[0]) :
                similar_movie = recom_movie[ (record_list['title'][i]) ].dropna().sort_values(ascending=False).to_frame()
                similar_movie.columns = ['corr']
                similar_movie['Weight'] = record_list['rating'][i] * similar_movie['corr']
                
                similar_movies_list = similar_movies_list.append(similar_movie)
            
            similar_movies_list.reset_index(inplace=True)
            similar_movies_list = similar_movies_list.groupby('title')['Weight'].max().sort_values(ascending=False)

            for movie in record_list['title']:
                if movie in similar_movies_list.index:
                    similar_movies_list.drop(movie, inplace=True)

            # 상위 10개 추출
            similar_movies_list = similar_movies_list.head(10)

            #JSON 형식으로 건네주기 위해 리스트화
            recom = list (similar_movies_list.index)

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
            
        return {'recom':recom}, HTTPStatus.OK