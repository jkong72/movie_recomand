import mysql.connector

def get_cnx() :
    cnx = mysql.connector.connect(
        host = 'learn-db.cbdfurkch0nx.ap-northeast-2.rds.amazonaws.com',
        database = 'movie_recoDB',
        user = 'movie_reco',
        password = '7913'
    )
    return cnx