from flask import Flask,request

app = Flask(__name__)

@app.route('/webhookcallback',methods=['POST'])
def hook():
    print(f"Received request: {request.json}")
    return "OK"
    

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=8080)