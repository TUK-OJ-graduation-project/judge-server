from flask import Flask, request
import os

app = Flask(__name__)

@app.route('/run', methods=['POST'])
def run_script():
    user_script = request.get_json()['script']
    with open('script.py', 'w') as file:
        file.write(user_script)
    os.system('python script.py')
    return 'Script executed successfully'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
