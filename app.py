from flask import Flask, request, jsonify
import os
import subprocess
import sys

app = Flask(__name__)

@app.route('/run', methods=['POST'])
def run_script():
    # user_script = request.get_json()['script']
    user_script = request.form['script']
    with open('script.py', 'w') as file:
        file.write(user_script)
    result = subprocess.run(['python', 'script.py'], text=True, capture_output=True)
    if result.returncode != 0:
        print(result.stderr, file=sys.stderr)
        return jsonify({"error": result.stderr})
    else:
        print(result.stdout)
        return jsonify({"output": result.stdout or "Executed successfully!"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
