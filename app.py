# flask 모듈 임포트
from flask import Flask, send_file, render_template, request

# 세션 기능을 위한 모듈
# from flask import session
# DB 파일 연결
# import db

import warnings
warnings.filterwarnings('ignore')
import pandas as pd


from bs4 import BeautifulSoup
# from fake_useragent import UserAgent
# import scrapy,response
import requests

from selenium import webdriver
import time
import folium
import json
import pymysql
import db
from folium.plugins import MarkerCluster
from folium import plugins
from folium.plugins import HeatMap

path = '/home/ubuntu/chromedriver'

options = webdriver.ChromeOptions()
options.add_argument('headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument("--disable-setuid-sandbox")

driver = webdriver.Chrome(executable_path=path, options=options)
# driver = webdriver.Chrome('data/chromedriver')
# flask 객체 생성
app = Flask(__name__)

# 세션을 위한 비밀키 설정
# app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

# 라우터 등록 => 웹상 루트 주소 생성

@app.route('/',methods=['get','post'])
def root():
    # print(request.method)
    # if request.args:
    if request.method == 'GET':
        if request.args:
            # print(request.args)

            req = request.args['q']
            name = request.args['name']
            url = 'static/images/' + req + '.png'
            # print(req)
            return render_template('root.html',req=req,name=name, url=url)
        else:
            return render_template('root.html',name='none')

    else:
        name = request.form['chk_info']
        options = request.form['options']
        name = name +' '+ options
        # print(name)
        return render_template('root.html',name=name)



@app.route('/ajax_get_item/<gu_name>')
def make_gu(gu_name):

    dong_result = db.dong_list(gu_name)
    json_data = json.dumps(dong_result,indent=4,ensure_ascii=False)
    return json_data

@app.route('/ajax_get_aptItem/<dong_name>')
def get_aptData(dong_name):

    apt_list = db.apt_list(dong_name)
    json_data = json.dumps(apt_list,indent=4,ensure_ascii=False)
    return json_data

@app.route('/ajax_get_aptInfo/<gu_id>/<dong_name>/<apt_name>')
def apt_Info(gu_id,dong_name,apt_name):
    gu_id = int(gu_id)
    driver.get("http://aptprice.drapt.com/list.php?type=1&si=%BC%AD%BF%EF%C6%AF%BA%B0%BD%C3")
    gu_ul = gu_id//5+1
    gu_li = gu_id%5+1
    xpath = '//*[@id="dangiDivArea"]/ul[' + str(gu_ul) + ']/li[' + str(gu_li) + ']/a'
    element_sel_gu = driver.find_element_by_xpath(xpath).click()
    dong_target = '#dangiDivArea > ul > li > a'
    dong_result = driver.find_elements_by_css_selector(dong_target)
    index = 0
    for i,v in enumerate(dong_result):
        if v.text == dong_name:
            index = i
            break
        # print(i.text)
        # print(v.text)
        # dicts = {'dong':v.text,'index':i}
        # dong_list.append(dicts)
    dong_ul = index//5+1
    dong_li = index%5+1
    xpath = '//*[@id="dangiDivArea"]/ul[' + str(dong_ul) + ']/li[' + str(dong_li) + ']/a'
    element_sel_gu = driver.find_element_by_xpath(xpath).click()
    apt_target = '#dangiDivArea > ul > li > a'

    apt_result = driver.find_elements_by_css_selector(apt_target)
    index1 = 0
    for i,v in enumerate(apt_result):
        if v.text == apt_name:
            index1 = i
            break
        # print(v.text)
        # dicts = {'apt':v.text,'index':i}
        # apt_list.append(dicts)
        # apt_list.append(i.text)
    # get_aptData(gu_id,dong_id)
    # apt_id = int(apt_id)
    apt_ul = index1 // 4 + 1
    apt_li = index1 % 4 + 1
    xpath = '//*[@id="dangiDivArea"]/ul[' + str(apt_ul) + ']/li[' + str(apt_li) + ']/a'
    element_sel_gu = driver.find_element_by_xpath(xpath).click()
    cur_url = driver.current_url
    response = requests.get(cur_url)
    soup = BeautifulSoup(response.text, 'html.parser')

    table = soup.find('table', {'class': 'common_table02 mt10 tac'})
    infoPrint = []
    for i,a in enumerate(table.find_all("tr")):
        if i == 0:
            continue
        infolist = []
        for b in a.find_all("td"):
            info = b.get_text()
            infolist.append(info)
        dicts = {'info':infolist}
        infoPrint.append(dicts)

    # null list인 0번째 인덱스 삭제
    # del infoPrint[0]
    json_data = json.dumps(infoPrint,indent=4,ensure_ascii=False)

    return json_data


@app.route('/index/<name>')
def index(name):
    name.strip()
    geo_path = 'data/seoul_municipalities_geo_simple.json'
    geo_json = json.load(open(geo_path, encoding='utf-8'))
    gu_list = pd.read_csv('data/gu_lat_lng_list.csv', encoding='UTF-8', index_col='구')

    # folium_map = folium.Map(location=[geo_df['위도'].mean(), geo_df['경도'].mean()], zoom_start=12)
    folium_map = folium.Map(location=[37.561270,126.986230], zoom_start=11)
    if name == 'security':
        dbCrime_list = db.get_dbCrime_data()

        geo_df = pd.DataFrame(data=dbCrime_list)
        geo_df = geo_df.set_index('구별')
        folium_map.choropleth(geo_data=geo_json, data=geo_df['범죄'], columns=[geo_df.index, geo_df['범죄']],
                              fill_color='PuRd', key_on='feature.properties.SIG_KOR_NM', fill_opacity=0.7,line_opacity=0.2, highlight=True,legend_name='5대범죄발생 정규화 비율')
        for n in gu_list.index:
            if n == '강서구':
                continue
            folium.CircleMarker([gu_list.loc[n, '위도'], gu_list.loc[n, '경도']],radius=geo_df.loc[n,'범죄발생건수']/100, popup='범죄건수:'+str(geo_df.loc[n,'범죄발생건수']), color=None, fill=True,fill_opacity=0.8, fill_color='Blues').add_to(folium_map)

    elif 'store' in name:
        nameList = name.split()
        # print(nameList[0])
        # print(nameList[1])
        if nameList[1] == 'convenience':
            convenience_list = db.get_convenience_list()
            geo_df = pd.DataFrame(data=convenience_list)
            geo_df = geo_df.set_index('구별')
            folium_map.choropleth(geo_data=geo_json, data=geo_df['개수'], columns=[geo_df.index, geo_df['개수']],fill_color = 'Oranges', key_on='feature.properties.SIG_KOR_NM',fill_opacity=0.7, line_opacity=0.4, highlight=True,legend_name='편의점 개수')
        elif nameList[1] == 'mart':
            mart_list = db.get_mart_list()
            geo_df = pd.DataFrame(data=mart_list)
            geo_df = geo_df.set_index('구별')
            folium_map.choropleth(geo_data=geo_json, data=geo_df['개수'], columns=[geo_df.index, geo_df['개수']],fill_color='Blues', key_on='feature.properties.SIG_KOR_NM', fill_opacity=0.7,line_opacity=0.4, highlight=True,legend_name='마트 개수')
        movie_list = db.get_movie_list()
        geo_df_movie = pd.DataFrame(data=movie_list)
        data = geo_df_movie[['위도', '경도']].values
        MarkerCluster(data).add_to(folium_map)

        mc = MarkerCluster()
        for n in geo_df_movie.index:
            popup_name = geo_df_movie.loc[n, '영화관명']

            if geo_df_movie['영화관명'].str.contains('CGV')[n]:
                icon_color = 'red'
            elif geo_df_movie['영화관명'].str.contains('롯데')[n]:
                icon_color = 'orange'
            elif geo_df_movie['영화관명'].str.contains('메가')[n]:
                icon_color = 'darkblue'
            else:
                icon_color = 'black'

            folium.Marker([geo_df_movie.loc[n, '위도'],
                           geo_df_movie.loc[n, '경도']],
                          popup=popup_name,
                          icon=folium.Icon(color=icon_color))

            mc.add_child(folium.Marker([geo_df_movie.loc[n, '위도'],
                                        geo_df_movie.loc[n, '경도']],
                                       popup=popup_name,
                                       icon=folium.Icon(color=icon_color)))
        folium_map.add_child(mc)
        # else:
        #
    elif name == 'station':
        # station_list = db.get_seoul_station()
        # geo_df2 = pd.DataFrame(data=station_list)
        geo_df2 = pd.read_csv('data/seoul_station.csv')
        # print(geo_df2)
        data = geo_df2[['lat', 'lng']].values
        MarkerCluster(data).add_to(folium_map)
        mc = MarkerCluster()
        dbStation = db.get_station_list()
        geo_df = pd.DataFrame(data=dbStation)
        geo_df = geo_df.set_index('구별')
        folium_map.choropleth(geo_data=geo_json, data=geo_df['개수'], colmns=[geo_df.index, geo_df['개수']],
                              fill_color='YlGnBu', key_on='feature.properties.SIG_KOR_NM', fill_opacity=0.7,
                              line_opacity=0.2, highlight=True,legend_name='지하철역 개수')
        for n in geo_df2.index:
            # 팜업에 들어갈 텍스트를 지정해준다
            popup_name = geo_df2.loc[n, '역명'] + '역' + '\n \n ' + geo_df2.loc[n, '호선'] + '호선'
            if (geo_df2.loc[n, '호선'] == '1' or geo_df2.loc[n, '호선'] == '2' or geo_df2.loc[n, '호선'] == '3' or geo_df2.loc[
                n, '호선'] == '4' or geo_df2.loc[n, '호선'] == '5' or geo_df2.loc[n, '호선'] == '6' or geo_df2.loc[
                n, '호선'] == '7' or geo_df2.loc[n, '호선'] == '8' or geo_df2.loc[n, '호선'] == '9'):
                hosun_color = int(geo_df2.loc[n, '호선'])
            else:
                hosun_color = 10
            # 브랜드명에 따라 아이콘 색상을 달리해서 찍어준다.
            color_type = (
            '#FF0000', '#0B6121', '#FF8000', '#0174DF', '#8258FA', '#B45F04', '#808000', '#FF00BF', '#B18904',
            '#BDBDBD')

            icon_color = color_type[hosun_color - 1]

            folium.CircleMarker([geo_df2.loc[n, 'lat'], geo_df2.loc[n, 'lng']],
                                radius=3, popup=popup_name, color=None, fill=True,
                                fill_opacity=0.8, fill_color=icon_color).add_to(folium_map)

            mc.add_child(folium.CircleMarker([geo_df2.loc[n, 'lat'],
                                              geo_df2.loc[n, 'lng']],
                                             popup=popup_name,
                                             icon=folium.Icon(color=icon_color)))

        folium_map.add_child(mc)
    for n in gu_list.index:
        folium.CircleMarker([gu_list.loc[n, '위도'], gu_list.loc[n, '경도']], radius=6, popup=folium.Popup(
            '<a href="http://3.16.113.29/?q=' + n + '&name='+name+'" target="_top">' + n + '</a>',fill=True,fill_opacity=0.9)).add_to(
            folium_map)

    return folium_map._repr_html_()

# if __name__ == '__main__':
#     app.run(debug=True)


# 앱 실행  —> 마지막 위치 유지
# 웹주소와 포트 지정
app.run(host='0.0.0.0', port=80, debug=True)