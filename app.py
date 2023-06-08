from flask import Flask, request, jsonify
import os
import docker
import uuid

app = Flask(__name__)
app.debug = True # 오류 발생 확인을 위해 (프로덕션 환경에서는 보안 때문에X)

@app.route('/run', methods=['POST'])
def run_script():
    try:
        user_script = request.form['script']  # 사용자가 제출한 코드
        test_cases = request.form.get('test_cases', [])  # 기존 테스트케이스 받기
        
        # test_cases가 튜플 목록인지 확인
        if not isinstance(test_cases, list):
            raise ValueError("test_cases는 list여야 합니다.")
        for test_case in test_cases:
            if not isinstance(test_case, tuple) or len(test_case) != 2:
                raise ValueError("각 test_case는 정확히 두 요소의 튜플이어야 합니다.")
        
        result = run_code(user_script, test_cases)  # 코드 채점결과 반환
        return jsonify({"output": result or "Code executed successfully."})
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

def run_code(code, test_cases):
    try:
        client = docker.from_env()

        container = client.containers.run('my_python_judge', detach=True)

        # 여기서 사용자가 제출한 코드와 실제 문제의 테스트케이스와 비교해서 채점결과 반환
        code_with_tests = generate_code_with_tests(code, test_cases)
        
        # 각 요청에 대해 고유한 파일 이름 생성 (code.py에서 filename으로 바꿔줌.)
        filename = f"code_{uuid.uuid4()}.py"
        with open(filename, 'w') as f:
            f.write(code_with_tests)

        with open(filename, 'rb') as file_obj:
            _, _ = container.put_archive('/', file_obj)

        # 2>&1 : stderr(2)를 stdout(1)으로 리다이렉션 -> 실행 중인 프로그램에서 일반 출력과 오류 메시지를 모두 캡처하려는 경우 유용
        result = container.exec_run(f'python3 {filename} 2>&1', timeout=60)
        output = result.output
        return output.decode('utf-8')
    finally:
        # 코드 실행 후 파일 정리
        if os.path.exists(filename):
            os.remove(filename)

def generate_code_with_tests(code, test_cases):
    test_code = [
        """
def run_tests(f, test_cases):
    results = []
    for i, (input, expected_output) in enumerate(test_cases):
        try:
            # 문자열인 경우 입력을 따옴표로 묶어준다.
            if isinstance(input, str):
                input = f'"{input}"'
            result = f(input)
            if result == expected_output:
                results.append(f'Test case {i+1}: SUCCESS')
            else:
                results.append(f'Test case {i+1}: FAIL - Expected {expected_output}, but got {result}')
        except Exception as e:
            results.append(f'Test case {i+1}: ERROR - {str(e)}')
    return results
"""
    ]
    
    # 사용자의 코드를 추가
    test_code.append(code)

    # 사용자의 함수 및 테스트 케이스로 테스트 함수 호출
    test_code.append(f"print('\\n'.join(run_tests(f, {test_cases})))")

    # 모든 것을 하나의 스크립트로 결합
    return '\n'.join(test_code)

# Flask 서버(앱) 실행
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80)