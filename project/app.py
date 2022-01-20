from PIL import Image, ImageOps

from flask import Flask, render_template, request, jsonify, redirect, url_for

import hashlib

import jwt
import datetime

import base64
import numpy as np
import io
import tensorflow as tf
# 사용하지 않는다고 써있지만 지우면 작동이 안되는 패키지 ;;;
from tensorflow.keras.models import Model

import requests
# from bs4 import BeautifulSoup

SECRET_KEY = '333'
app = Flask(__name__)
model = tf.keras.models.load_model('keras_model.h5')
# MongoDB 연결
from pymongo import MongoClient

client = MongoClient('mongodb+srv://test:sparta@cluster0.dsncs.mongodb.net/Cluster0?retryWrites=true&w=majority')
db = client.sparta


@app.route("/")
def home():
    return render_template('main.html')


@app.route("/main", methods=['GET'])
def makgeolli_get():
    # print(1)
    makgeolli_list = list(db.Makgeolli.find({}, {'_id': False}))
    print(makgeolli_list)
    print(makgeolli_list[0]['mak_info'])
    # print(makgeolli_list['mak_star_avg'])
    return jsonify({'makgeollis': makgeolli_list})


@app.route("/main", methods=['POST'])
def mak_info_ajax():
    mak_id = request.form.get("mak_id")
    print(mak_id)
    makgeolli_list = db.Makgeolli.find_one({'mak_id': int(mak_id)}, {'_id': False})
    print(makgeolli_list['mak_info'])
    # print(makgeolli_list['mak_star_avg'])
    return jsonify({'result': makgeolli_list})


@app.route("/join", methods=['GET', 'POST'])
def join():
    if request.method == 'POST':
        name_receive = request.form['name_give']
        birth_receive = request.form['birth_give']
        id_receive = request.form['id_give']
        pw_receive = request.form['pw_give']
        email_receive = request.form['email_give']

        pw_hash = hashlib.sha256(pw_receive.encode('utf-8')).hexdigest()
        doc = {
            'user_name': name_receive,
            'user_birth': birth_receive,
            'user_id': id_receive,
            'user_pw': pw_hash,
            'user_email': email_receive
        }
        db.User.insert_one(doc)
        return jsonify(True)
    else:  # GET 이면
        return render_template('join.html')


@app.route("/id_check", methods=["POST"])
def id_post():
    id_receive = request.form['id_give']
    id_list = list(db.User.find({}, {'_id': False}))
    # db.User.find_one({'user_ID':id_receive})
    user_id = []

    for person in id_list:
        value = person['user_id']
        user_id.append(value)

    if id_receive in user_id:  # 중복된 아이디일 경우
        return jsonify(True)
    else:  # 중복되지 않는 아이디일 경우
        return jsonify(False)


##로그인 페이지
@app.route("/login")
def login():
    return render_template('login.html')


@app.route("/login", methods=["POST"])
def login_post():
    id_receive = request.form['id_give']
    password_receive = request.form['password_give']
    pw_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()

    result = db.User.find_one({'user_id': id_receive, 'user_pw': pw_hash})
    if result is not None:
        payload = {
            'user_id': id_receive,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=50)
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
        return jsonify({'result': 'success', 'token': token})
    else:
        return jsonify({'result': 'fail', 'msg': '아이디/비밀번호가 일치하지 않습니다.'})


# comment 하는중 =====
# /*{mak_name, mak_img_url, mak_info, mak_star_avg, comment, comment_user_id, comment_id, comment_star_score}*/
@app.route("/comment", methods=['GET'])
def comments():
    mak_id = request.args.get('mak_id')
    my_user_id = request.cookies.get('mytoken')
    print(mak_id)
    try:
        payload = jwt.decode(my_user_id, SECRET_KEY, algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="로그아웃 되었습니다. 다시 로그인 해주세요."))

    if mak_id is None:
        return render_template('main.html')

    com = list(db.Comment.find({'mak_ref_id': int(mak_id)}, {'_id': 0}).sort('comment_id', -1))
    mak1 = db.Makgeolli.find_one({'mak_id': int(mak_id)}, {'_id': 0})
    db.Makgeolli.update_one({'mak_id': int(mak_id)}, {'$set': {'mak_star_avg': int(star_avg(com))}})
    return render_template('comment.html', comments=com, mak=mak1, user_id=payload['user_id'], mak_id=mak_id,
                           avg=int(star_avg(com)))


# comment_id , mak_ref_id, comment_user_id, comment, comment_star_score, comment_creatat
@app.route("/comment", methods=['POST'])
def comment_insert():
    get_comment_id = seq_comment_id()
    mak_ref_id = request.form['mak_ref_id']
    comment_id = get_comment_id['val']
    comment_user_id = request.form['comment_user_id']
    comment = request.form['comment']
    comment_star_score = request.form['star_score']
    comment_creat_at = datetime.datetime.now()
    doc = {
        'comment_id': comment_id,
        'mak_ref_id': int(mak_ref_id),
        'comment_user_id': comment_user_id,
        'comment': comment,
        'comment_star_score': comment_star_score,
        'comment_creat_at': comment_creat_at
    }
    # 입력
    db.Comment.insert_one(doc)
    # print(comment, comment_star_score, comment_creat_at, comment_user_id, comment_id, type(mak_ref_id))
    # 결론적으로 새로고침 해당 게시판으로 이동
    return redirect('/comment?mak_id=' + mak_ref_id)


# 코멘트 숫자를 관리하기 위한 시퀀스 테이블
def seq_comment_id():
    #     # comment_id의 숫자를 1씩 더해주는 시퀀스
    db.Seq.update_one({'name': 'comment_id'}, {'$inc': {'val': 1}})
    # 그 시퀀스로 더해서 변경된 comment_id를 가져오는 부분
    return db.Seq.find_one({'name': 'comment_id'}, {'_id': 0, 'name': 0})


# 별점 평균 구하는 식
def star_avg(com):
    star_score = 0
    for i in com:
        star_score += int(i['comment_star_score'])
    # star_score 가 0점 댓글이 하나 없을때 오류를 빠져나오는 try문
    try:
        return round(star_score / len(com), 1)
    except ZeroDivisionError:
        return 0


@app.route("/comment/delete", methods=["GET"])
def comment_del():
    mak_ref_id = request.args.get('mak_id')
    comment_id = request.args.get('comment_id')
    print(comment_id)
    print(comment_id)
    db.Comment.delete_one({'comment_id': int(comment_id)})
    print(comment_id)
    print(mak_ref_id)
    return redirect('/comment?mak_id=' + mak_ref_id)


# comment 하는중 =====


# request 페이지
@app.route("/request")
def requst():
    return render_template('request.html')


@app.route("/request", methods=["POST"])
def request_post():
    print(1)
    userid = request.form['userid_give']
    makname = request.form['makname_give']
    makfile = request.files['makfile_give']
    # print(type(makfile))
    request_receive = request.form['request_give']
    # print(request_receive)
    #쿠키가져와 로그인한 id와 id입력란에 적은 id가 일치한지 확인
    token_receive = request.cookies.get('mytoken')
    #가져온 파일 저장
    filename=makfile.filename #filename만 가져오기
    print(filename)
    makfile.save(f'static/request_img/{filename}')  #우리 데이터에 경로지정하여 사진 저장

    # print(token_receive)
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.User.find_one({"user_id": payload['user_id']},{'_id': 0})
        # print(user_info['user_name'])
        # 같을경우 db에 저장후 완료처리

        if user_info['user_id']==userid:
            doc = {
                "userid": userid,
                "makname": makname,
                "makfileurl": filename,
                "request": request_receive
            }
            db.Recommend.insert_one(doc)
            return jsonify({'result':'success','msg': userid + "님의 추천막걸리가 요청되었습니다."})
        else: #다를경우 본인아이디가 아님을 알림
            return jsonify({'result':'check','msg': "본인의 id를 입력해주세요."})

    except jwt.ExpiredSignatureError:
        return jsonify({'result': 'fail', 'msg': '로그인 시간이 만료되었습니다.'})
    except jwt.exceptions.DecodeError:
        return jsonify({'result': 'fail', 'msg': '로그인 정보가 존재하지 않습니다.'})

@app.route("/camera", methods=['GET'])
def camera():
    my_user_id = request.cookies.get('mytoken')

    try:
        payload = jwt.decode(my_user_id, SECRET_KEY, algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="로그아웃 되었습니다. 다시 로그인 해주세요."))
    return render_template('camera.html')




@app.route("/camera_test", methods=['GET'])
def test_camera():
    print("테스트다 에헷")
    return render_template('camera_test.html')



@app.route("/camera_test", methods=['POST'])
def test_camera_test():
    data = request.form.get('data')
    # print("이얍 받아라 나의 데이터를")
    data = data.split(',')[1]
    imgdata = base64.b64decode(data)
    data = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)
    image = Image.open(io.BytesIO(imgdata))
    size = (224, 224)
    image = ImageOps.fit(image, size, Image.ANTIALIAS)
    image_array = np.asarray(image)
    # Normalize the image
    normalized_image_array = (image_array.astype(np.float32) / 127.0) - 1
    # Load the image into the array
    data[0] = normalized_image_array
    prediction = model.predict(data)
    # print(np.around(prediction, 8))
    label = np.array([['톡쏘는 알밤 동동 막걸리', '경주법주 쌀 막걸리', '인천 소성주 생 막걸리', '장수 생 막걸리', '지평 막걸리', '인식 중입니다. 가까이오세요']])
    # ['톡쏘는 알밤 동동 막걸리', '경주법주 쌀 막걸리', '인천 소성주 생 막걸리', '장수 생 막걸리', '지평 막걸리', '인식 중입니다. 가까이오세요']
    # ['albam', 'gyeongju', 'jangsu', 'jipyeong', 'sosungju' , '인식중입니다.']
    print(label[prediction[:] > 0.5])
    mak_id = np.array([['30', '50', '40', '20', '10', '0']])
    print(mak_id[prediction[:] > 0.5])
    return jsonify({'msg': label[prediction[:] > 0.5][0], 'mak_id': mak_id[prediction[:] > 0.5][0]})


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
