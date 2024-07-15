from flask import Flask,request

app = Flask(__name__)

@app.route('/webhookcallback',methods=['POST'])
def hook():
    print(f"Received request: {request.json}")
    return "OK"
    

if __name__ == '__main__':
    app.run(host='127.0.0.1',port=8080)