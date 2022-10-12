from cgitb import reset
from re import search
from turtle import down
from flask import Flask, jsonify, request, json, request_tearing_down, redirect,send_file
import urllib.request
import requests
from moviepy.editor import *
import os
import pymysql
import base64

path:str = os.path.dirname(os.path.realpath(__file__)) 
download_dic_name = '/download_temp' 
convert_dic_name = '/convert_temp'
app = Flask(__name__)


### DB CONNECTION ###
db = pymysql.connect(
    host='', 
    port=3306, 
    user='root', 
    passwd='', 
    db='API', 
    charset='utf8'
    )

def search_cache_data_num(url:str):
    db.connect()
    cur = db.cursor(pymysql.cursors.DictCursor)
    sql = 'SELECT no FROM convert_cache WHERE target_url = "{0}"'.format(url)
    cur.execute(sql)
    res = cur.fetchall()
    if len(res) == 0:
        return None

    print(res[0])
    return res[0]['no']

def search_cache_data_for_num(num:int):
    db.connect()
    cur = db.cursor(pymysql.cursors.DictCursor)
    print(num)
    sql = 'SELECT data FROM convert_cache WHERE no={0}'.format(num)
    cur.execute(sql)
    res = cur.fetchall()
    if len(res) == 0:
        return None

    print(res[0])
    return res[0]['data']

def insert_cache_data(url:str, filePath:str):
    f = open(filePath, 'rb')
    db.connect()
    cur = db.cursor(pymysql.cursors.DictCursor)
    sql = 'INSERT INTO convert_cache(type, target_url, data, update_time) VALUES(%s, %s, %s, current_timestamp())'
    with open(filePath, 'rb') as file:
        bData = file.read()
        
    arg = (0, url, bData)
    cur.execute(sql, arg)
    db.commit()
    return True


### DB CONNECTION OUT ###

def check_path_provider():
    if not 'download_temp' in getScriptFileLists():
        print('making new dic -> download_temp')
        os.mkdir(path +download_dic_name)
    
    if not 'convert_temp' in getScriptFileLists():
        print("making new dic -> convert_temp")
        os.mkdir(path +convert_dic_name)

def getScriptFileLists():
    return os.listdir(path)

def download_temp_file_list():
    return os.listdir(path+download_dic_name)

def conv_temp_file_list():
    return os.listdir(path+convert_dic_name)

def mp4_to_gif(mp4_path:str):
    fileName = get_last_num_in_convert_temp()
    print(mp4_path +'/////' +fileName)
    VideoFileClip(mp4_path).speedx(8).write_gif(fileName)
    return fileName

def download_mp4(url:str, path:str):
    try:
        res = requests.get(url)

        f=open( path ,'wb');
        for chunk in res.iter_content(chunk_size=255): 
            if chunk: # filter out keep-alive new chunks
                f.write(chunk)
        f.close()
    except Exception as e:
        print('some error when download mp4 -> {0}'.format(e))
        return ""
    

    return path

def get_last_num_in_download_temp():
    stack:int = 0
    lstData = download_temp_file_list()
    if len(lstData) == 0:
        return "{0}.mp4".format(0)
    for i in  download_temp_file_list():
        if stack < int(i.replace(".mp4",'')):
            stack = int(i.replace(".mp4", ''))
        print(i)
    return "{0}.mp4".format(stack+1)

def get_last_num_in_convert_temp():
    stack:int = 0
    lstData = conv_temp_file_list()
    if len(lstData) == 0:
        return path+convert_dic_name+"/{0}.gif".format(0)
    for i in  conv_temp_file_list():
        if stack < int(i.replace(".gif",'')):
            stack = int(i.replace(".gif", ''))
        print(i)

    d =  "{0}.gif".format(path+convert_dic_name+'/'+str(stack+1))
    return d

@app.route('/getconvertdata', methods=['GET'])
def getConvertData():
    req = request.args.get('num')
    if req == None:
        res = search_cache_data_for_num(0)

    try:
        i = int(req)
        if search_cache_data_for_num(i) == None: res = search_cache_data_for_num(0)
        else : res = search_cache_data_for_num(i)
    except Exception as e:
        res = search_cache_data_for_num(0)
    
    with open('{0}{1}/dump.gif'.format(path, convert_dic_name), 'wb') as fh:
        fh.write(res)
    
    return send_file('{0}{1}/dump.gif'.format(path, convert_dic_name), 'image/gif')


@app.route('/convertmp4togif', methods=['POST'])
def conv():
    objPostData = request.values.to_dict()
    if not 'url' in objPostData : return json.dumps({'res' : 'err', 'value' : 'url is not valid in post data'})

    urlTemp:str = objPostData['url'].split('/')
    urlTemp = urlTemp[len(urlTemp)-1]
    
    nNum = search_cache_data_num(objPostData['url'])
    if nNum == None:
        downRes = download_mp4(objPostData['url'], path+download_dic_name+'/' +get_last_num_in_download_temp())
        if downRes == False:
            return json.dumps({'res' : 'err', 'value' : 'some err'})
        convRes = mp4_to_gif(downRes)
        insert_cache_data(objPostData['url'], convRes)
    
    return {'res' : 'ok', 'value' : '/getconvertdata?num={0}'.format(nNum)}
    

    # 학교 과제단
@app.route('/getconvertdata', methods=['GET'])
def getConvertData():
    req:dict = request.args.get
    if not 'msg' in req.keys:
        return json.dumps({'res' : 'err', 'value' : 'need msg in get data'})
    
    return request.args.get['msg']

if __name__ == '__main__':
    
    app.run(host='0.0.0.0', port=8080, debug=True)