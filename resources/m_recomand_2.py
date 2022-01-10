from flask_jwt_extended.utils import get_jwt_identity
from flask_jwt_extended.view_decorators import jwt_required
from flask import request
from flask_restful import Resource
from http import HTTPStatus
from mysql.connector.errors import Error
import pandas as pd

from utils_MySQL_connection import get_cnx

# 자동으로 상관관계를 업데이트하고 movie_id를 사용하는
class AdvancedMovieRecommandResource(Resource):
    @jwt_required() # 헤더를 통해 토큰을 받음
    def get (self):
        user_id = get_jwt_identity()
        try:
            cnx = get_cnx()
            
            # 특정 기간마다 영화의 상관관계를 갱신
            # if True:
            #     pass

            # movie 데이터테이블 가져오기
            query = '''select *
                        from movie'''

            cursor = cnx.cursor(dictionary = True)
            cursor.execute(query)
            record_list = cursor.fetchall()

            movie_list = record_list


            # rating 데이터테이블 가져오기
            query = '''select *
                        from rating'''

            cursor = cnx.cursor(dictionary = True)
            cursor.execute(query)
            record_list = cursor.fetchall()

            rating_list = record_list

            # 데이터프레임화
            movie_df = pd.DataFrame(movie_list)
            rating_df = pd.DataFrame(rating_list)

            # 필요한 데이터만 추출
            movie_df = movie_df[['id', 'title']]
            rating_df = rating_df.iloc[:,1:3+1]

            # merge 기준열로 사용하기 위해 컬럼이름 변경
            movie_df.columns = ['movie_id', 'title']

            # 두 데이터를 합치기
            movies_rating_df = pd.merge(rating_df, movie_df, how='left', on='movie_id')

            # 피벗테이블 활용해 영화간 상관관계 분석
            userid_movietitle_matrix = pd.pivot_table(movies_rating_df,
                                                        index = 'user_id',
                                                        columns = 'movie_id',
                                                        values = 'rating',
                                                        aggfunc = 'mean')

            recom_movie = userid_movietitle_matrix.corr()                            


            # 실제 추천 부분
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
            rating = cursor.fetchall()

            # 데이터프레임화
            rating = pd.DataFrame(rating)

            # 유저가 평가한 영화를 바탕으로
            # 상관관계를 파악하고, 평가를 가중치로 곱함.
            similar_movies_list = pd.DataFrame()
            for i in range(rating.shape[0]) :
                similar_movie = recom_movie[ (rating['movie_id'][i]) ].dropna().sort_values(ascending=False).to_frame()
                similar_movie.columns = ['corr']
                similar_movie['Weight'] = rating['rating'][i] * similar_movie['corr']
                
                similar_movies_list = similar_movies_list.append(similar_movie)
            
            # 중복 제거
            similar_movies_list.reset_index(inplace=True)
            # 영화 선택에는 복합적인 요소에 영향을 받으므로
            # 중복되는 데이터는 평균을 구해서 계산.
            similar_movies_list = similar_movies_list.groupby('movie_id')['Weight'].mean().sort_values(ascending=False)

            # 이미 평가한 영화 제거
            for movie in rating['movie_id']:
                if movie in similar_movies_list.index:
                    similar_movies_list.drop(movie, inplace=True)

            # 상위 10개 추출
            similar_movies_list = similar_movies_list.head(10)

            query = '''select *
                        from movie
                        where id = %s'''

            recom_list = []
            for movie_id in similar_movies_list.index:
                param = (movie_id, )
                cursor = cnx.cursor(dictionary = True)
                cursor.execute(query, param)
                recom = cursor.fetchall()
                recom[0]['year'] = recom[0]['year'].isoformat()

                recom_list.append(recom[0])



            print ('-' *15)
            print (recom_list)

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
            
        return {'count': len(recom_list), 'recom':recom_list}, HTTPStatus.OK