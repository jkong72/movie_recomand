from flask import Flask
from flask_restful import Api
from flask_jwt_extended import JWTManager
from config import Config
from resources.u_info import UserInformationResource
from resources.u_login import UserLoginResource
from resources.u_logout import LogoutResource, jwt_blacklist
from resources.u_register import UserRegisterResource

app = Flask(__name__)
app.config.from_object(Config)
jwt = JWTManager(app)

@jwt.token_in_blocklist_loader  # 로그아웃 된 (블락리스트에 포함된)
                                # id 인지 확인함
def check_if_token_is_revoked(jwt_header, jwt_payload):
    jti = jwt_payload['jti']
    return jti in jwt_blacklist

api = Api(app)

api.add_resource(UserRegisterResource, '/api/v1/user/register') # 회원가입
api.add_resource(UserLoginResource,'/host/api/v1/user/login') #로그인
api.add_resource(LogoutResource, '/api/v1/user/logout') #로그아웃\
api.add_resource(UserInformationResource, '/api/v1/user/me')



if __name__ == "__main__":
    app.run()