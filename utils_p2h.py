from passlib.hash import pbkdf2_sha256

# 원문 비밀번호를 안호화하는 함수
def hash_password(password):
    # 솔트는 암호화의 기준역할을 하므로
    # 같은 솔트를 가진 해쉬의 패턴은 동일해지며
    # 이 경우 보안에 취약해지므로
    # 공개되어서는 안된다.
    salt = '59r4o64n51n2n13y6e678g8e27v44e33a76g94i51v654o77u89p'
    password = password + salt
    return pbkdf2_sha256.hash(password)

# 비밀번호의 일치성을 확인하는 함수
# password : 유저가 입력한 비밀번호
# hashed : 최초에 입력된 암호화된 비밀번호
# password를 같은 salt로 암호화해 hashed와의 일치여부를 검사하고
# 그 결과를 불리언으로 반환한다.
def check_password(password, hashed) :
    salt = '59r4o64n51n2n13y6e678g8e27v44e33a76g94i51v654o77u89p'
    return pbkdf2_sha256.verify(password+salt, hashed)
    