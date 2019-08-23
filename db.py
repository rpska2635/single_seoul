# 데이타베이스 관리 파일
import pymysql

# 데이타베이스 접속 함수
def get_connection():
    conn = pymysql.connect(host='database-2.clxwdlsberhc.us-east-2.rds.amazonaws.com',user = 'root',password = '12341234',db='project',charset='utf8')
    return conn

def dong_list(gu_name):
    conn = get_connection()
    cursor = conn.cursor()
    sql = 'select 동이름 from crawling_dong where 구이름 = %s'
    cursor.execute(sql,(gu_name,))
    resultSet = cursor.fetchall()
    dong_list = []
    for i in resultSet:
        dict = {'dong':i[0]}
        dong_list.append(dict)
    # result = {gu_name:dong_list}
    return dong_list

def apt_list(dong_name):
    conn = get_connection()
    cursor = conn.cursor()
    sql = 'select 매물 from crawling_apt where 동이름 = %s'
    cursor.execute(sql,(dong_name,))
    resultSet = cursor.fetchall()
    apt_lists = []
    for i in resultSet:
        dict = {'apt':i[0]}
        apt_lists.append(dict)
    # result = {gu_name:dong_list}
    return apt_lists

def get_station_list():
    conn = get_connection()
    cursor = conn.cursor()
    sql = 'select * from station_gu;'
    cursor.execute(sql)
    result_list = cursor.fetchall()
    gu_list = []
    count_list = []
    for n in result_list:
        gu_list.append(n[1])
        count_list.append(n[2])
    result = {'구별':gu_list, '개수':count_list}
    conn.close()
    return result

def get_seoul_station():
    conn = get_connection()
    cursor = conn.cursor()
    sql = 'select 호선,역명,구별,lat,lng from seoul_station;'
    cursor.execute(sql)
    result_list = cursor.fetchall()
    ho_list = []
    name_list = []
    gu_list = []
    lat_list = []
    lng_list = []
    for n in result_list:
        ho_list.append(n[0])
        name_list.append(n[1])
        gu_list.append(n[2])
        lat_list.append(n[3])
        lng_list.append(n[4])
    result = {'호선':ho_list,'역명':name_list,'구별':gu_list,'lat':lat_list,'lng':lng_list}
    conn.close()
    return result

def get_dbCrime_data():
    conn = get_connection()
    cursor = conn.cursor()
    sql = "select 구별,범죄,범죄발생건수,CCTV from dbCrime;"
    cursor.execute(sql)
    db_list = cursor.fetchall()
    gu_list = []
    crime_list = []
    crime_data_list = []
    cctv_list = []
    for n in db_list:
        gu_list.append(n[0])
        crime_list.append(n[1])
        crime_data_list.append(n[2])
        cctv_list.append(n[3])
    result_list = {'구별': gu_list, '범죄': crime_list, '범죄발생건수': crime_data_list, 'CCTV': cctv_list}
    cursor.close()

    return result_list

def get_convenience_list():
    conn = get_connection()
    cursor = conn.cursor()
    sql = 'select * from convenience_gu;'
    cursor.execute(sql)
    resultSet = cursor.fetchall()
    gu_list = []
    count_list = []
    for i in resultSet:
        gu_list.append(i[1])
        count_list.append(i[2])
    result_list = {'구별':gu_list,'개수':count_list}
    cursor.close()
    return result_list

def get_mart_list():
    conn = get_connection()
    cursor = conn.cursor()
    sql = 'select * from mart_gu;'
    cursor.execute(sql)
    resultSet = cursor.fetchall()
    gu_list = []
    count_list = []
    for i in resultSet:
        gu_list.append(i[1])
        count_list.append(i[2])
    result_list = {'구별':gu_list,'개수':count_list}
    cursor.close()
    return result_list

def get_movie_list():
    conn = get_connection()
    cursor = conn.cursor()
    sql = 'select 영화관명,위도,경도 from movie_Seoul;'
    cursor.execute(sql)
    resultSet = cursor.fetchall()
    movie_list = []
    lat_list = []
    lng_list = []
    for i in resultSet:
        movie_list.append(i[0])
        lat_list.append(i[1])
        lng_list.append(i[2])
    result_list = {'영화관명':movie_list,'위도':lat_list,'경도':lng_list}
    cursor.close()
    return result_list
# 터미널에서 확인 python db.py



# 회원가입 테스트 - python db.py
# addDb_member('testtest','12345678')
# print(get_member_list())
