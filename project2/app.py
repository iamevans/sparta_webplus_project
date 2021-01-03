from flask import Flask, render_template, request, jsonify, redirect, url_for
from pymongo import MongoClient
import requests

app = Flask(__name__)

client = MongoClient('localhost', 27017)
db = client.dbsparta_plus_week2

@app.route('/')
def main():
    # DB에서 저장된 단어 찾아서 HTML에 나타내기
    msg = request.args.get("msg")
    words = list(db.words.find({}, {"_id": False}))
    return render_template("index.html", words=words, msg=msg)

@app.route('/detail/<keyword>')
def detail(keyword):
    status_receive = request.args.get("status_give", "old")
    # API에서 단어 뜻 찾아서 결과 보내기
    r = requests.get(f"https://owlbot.info/api/v4/dictionary/{keyword}", headers={"Authorization": "Token 990c8653785cd4bf04ba012237c7f0ba3d49b50f"})
    if r.status_code != 200:
        return redirect(url_for("main", msg="Word not found in dictionary; Try another word"))
    result = r.json()
    print(result)
    for definition in result["definitions"]:
        definition["definition"] = definition["definition"].encode('ascii', 'ignore').decode('utf-8')
        if definition["example"] is not None:
            definition["example"] = definition["example"].encode('ascii', 'ignore').decode('utf-8')
    return render_template("detail.html", word=keyword, result=result, status=status_receive)

@app.route('/api/save_word', methods=['POST'])
def save_word():
    # 단어 저장하기
    word_receive = request.form['word_give']
    definition_receive = request.form['definition_give']
    doc = {"word": word_receive, "definition": definition_receive}
    db.words.insert_one(doc)
    return jsonify({'result': 'success', 'msg': f'word "{word_receive}" saved'})

@app.route('/api/delete_word', methods=['POST'])
def delete_word():
    # 단어 삭제하기
    word_receive = request.form['word_give']
    print(word_receive)
    db.words.delete_one({"word":word_receive})
    return jsonify({'result': 'success', 'msg': f'word "{word_receive}" deleted'})

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
