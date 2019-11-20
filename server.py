from flask import Flask,render_template,request
from random import *
import json
import csv
from collections import OrderedDict
from bert_serving.client import BertClient
from scipy import spatial
from tqdm import tqdm
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/test')
def test():
    test_index = randint(1,31)
    return render_template('test.html',index= test_index,data = get_data_index(test_index-1))

@app.route('/info')
def inof():
    return "info"

@app.route('/result',methods=['GET','POST'])
def result():
    id = request.args.get('id')
    sentence = request.args.get('sentence')
    return compare_sentence(sentence, id)

def get_data_index(index):
    with open('static/data/koreanData.json') as data_file:
        data =json.load(data_file)
    return data["data"][index]

# 문장 안에 keyword가 얼마나 포함되어있는지 반환하는 함수
def how_many_keyword_in_sentence(sentence, keyword):
    add_base = 1/float(len(keyword))
    keyword_result = 0.0

    for content in keyword:
        # keyword가 문장에 포함되는 여부 => nltk 사용해야함
        if content in sentence:
            keyword_result += add_base
    return keyword_result


def compute_similarity(user_sentence, img_sentence, img_obj):
    v1 = BertClient().encode([user_sentence])
    v2 = BertClient().encode([img_sentence])
    print(user_sentence, img_sentence)
    
    cosine_distance = 1 - spatial.distance.cosine(v1[0], v2[0])
    cosine_distance = cosine_distance*0.5

    content_rate = how_many_keyword_in_sentence(user_sentence, img_obj)
    content_rate = content_rate*0.5
    print(cosine_distance, content_rate)

    similarity = cosine_distance + content_rate
    return similarity
    
    
'''
 @function: 사용자의 문장을 주어진 이미지의 다른문장과 비교
 @parameter:
    1. user_sentence = 사용자 문장
    2. img_id = 현재 사용자가 보고 있는 image의 id
 @return value: id를 가진 image의 모든 문장에 대한 비교 값
'''
def compare_sentence(user_sentence, img_id):
    # json file open
    file_handle = open('static/data/koreanData.json','r',encoding='utf-8')
    json_data = file_handle.read()
    file_handle.close()

    # json data를 dictionary로 변환
    try:
        dicts = json.loads(json_data)
    except:
        print('Don\'t convect json to dictionary in compare_sentence()')
        quit()

    img_sentence = dicts["data"][int(img_id) - 1]["sentence"]
    img_obj = list()
    
    # 객체의 value를 img_obj에 저장
    for img_val in dicts['data'][int(img_id) - 1]['object']:
        img_obj.append(img_val['value'])
    
    result = dict()
    max_similarity = -1
    sentence_list = list()

    # image의 각 문장들과 비교
    for sentence in img_sentence:
        temp_dict = dict()
        similarity = compute_similarity(user_sentence, sentence, img_obj)
        temp_dict['sentence'] = sentence
        temp_dict['score'] = round(similarity * 100, 2)
        sentence_list.append(temp_dict)

        if max_similarity < similarity: max_similarity = similarity
    
    result['totalScore'] = round(max_similarity * 100, 2)
    result['detail'] = sentence_list

    return json.dumps(result)


if __name__ == '__main__':
    app.run()