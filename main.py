import mysql.connector
from flask import Flask, send_from_directory, request, jsonify, Response
from flask_cors import CORS
from mysql_helper import MySQLHelper
import random
import string
import datetime
import smtplib
from email.mime.text import MIMEText
from email.utils import formataddr
from flask import make_response
import secrets
from openai import OpenAI
import os

app = Flask(__name__, static_folder='../../vue/chatcbd/vue-chatcbd/dist')
CORS(app)  # 启用CORS

db_helper = MySQLHelper(
    host='your_host',
    user='your_user',
    password='your_password',
    database='your_database'
) # 初始化数据库连接

@app.route('/<path:path>')
def static_proxy(path):
    # 处理所有静态文件请求
    return send_from_directory(app.static_folder, path)

@app.route('/', defaults={'path': ''})
def catch_all(path):
    if path and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/UserLogin')
def UserLogin():
    return send_from_directory(app.static_folder, 'index.html')
@app.route('/UserRegister')
def UserRegister():
    return send_from_directory(app.static_folder, 'index.html')
@app.route('/UserResetPassword')
def UserResetPassword():
    return send_from_directory(app.static_folder, 'index.html')
@app.route('/Chat')
def Chat():
    return send_from_directory(app.static_folder, 'index.html')


# 发送邮件函数
def send_email(receiver_email, code):
    # 发件人信息
    sender_email = ""  # 替换为你的QQ邮箱
    sender_name = ""  # 发件人名称
    smtp_server = ""  # QQ邮箱的SMTP服务器地址
    smtp_port = 465  # QQ邮箱的SMTP端口（SSL加密）
    smtp_password = ""  # 替换为你的QQ邮箱授权码

    # 邮件内容
    subject = "验证码邮件"
    body = f"""
    <html>
    <body style="font-family: Arial, sans-serif; background-color: #f4f4f9; padding: 20px;">
        <div style="max-width: 600px; margin: 0 auto; background-color: #ffffff; padding: 20px; border-radius: 8px; box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);">
            <h2 style="color: #007bff; text-align: center;">尊敬的用户</h2>
            <p style="font-size: 16px; color: #333333;">感谢您使用我们的服务。您的验证码如下：</p>
            <p style="font-size: 24px; font-weight: bold; color: #001f3f; text-align: center; background-color: #e0f7fa; padding: 10px; border-radius: 4px;">{code}</p>
            <p style="font-size: 16px; color: #333333;">请在5分钟内完成验证。</p>
            <br>
            <p style="font-size: 16px; color: #333333;">此致，</p>
            <p style="font-size: 16px; color: #007bff; text-align: right;">chatCBD 团队</p>
        </div>
    </body>
    </html>
    """

    # 创建邮件对象
    message = MIMEText(body, "html", "utf-8")
    message["From"] = formataddr((sender_name, sender_email))  # 发件人名称和邮箱
    message["To"] = receiver_email  # 收件人邮箱
    message["Subject"] = subject  # 邮件主题

    try:
        # 创建SMTP连接（使用SSL加密）
        with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
            server.login(sender_email, smtp_password)  # 登录QQ邮箱
            server.sendmail(sender_email, receiver_email, message.as_string())  # 发送邮件
        return True
    except Exception as e:
        print(f"Error: {e}")
        return True

@app.route('/api/send-captcha', methods=['POST'])
def send_captcha():
    data = request.json
    username = data.get('username')
    email = data.get('email')
    type = data.get('type')
    
    # 生成6位随机验证码
    captcha = ''.join(random.choices(string.ascii_letters + string.digits, k=6))
    timestamp = datetime.datetime.now()

    if type == 'register':
        try:
            # 查询数据库中是否存在该邮箱
            existing_entry = db_helper.fetch_one("SELECT * FROM verification_codes WHERE BINARY email = %s", (email,))
            
            if existing_entry:
                # 更新数据库中该邮箱对应的验证码和生成时间
                db_helper.execute_query(
                    "UPDATE verification_codes SET captcha = %s, created_at = %s WHERE BINARY email = %s",
                    (captcha, timestamp, email)
                )
            else:
                # 插入新数据到数据库中
                db_helper.execute_query(
                    "INSERT INTO verification_codes (email, captcha, created_at) VALUES (BINARY %s, %s, %s)",
                    (email, captcha, timestamp)
                )
        except Exception as e:
            return jsonify({"success": "no", "error": "Database error. Please try again."})
    elif type == 'reset-password':
        try:
            # 查询数据库中是否存在该用户
            existing_entry = db_helper.fetch_one("SELECT * FROM users WHERE BINARY username = %s", (username,))

            if existing_entry:
                email = existing_entry[2]
                # 更新数据库中该用户的邮箱对应的验证码和生成时间
                db_helper.execute_query(
                    "UPDATE verification_codes SET captcha = %s, created_at = %s WHERE BINARY email = %s",
                    (captcha, timestamp, email)
                )
            else:
                return jsonify({"success": "no", "error": "Invalid username. Please try again."})
        except Exception as e:
            return jsonify({"success": "no", "error": "Database error. Please try again."})
    
    # 发送邮件
    if send_email(email, captcha):
        return jsonify({"success": "yes"})
    else:
        return jsonify({"success": "no", "error": "Failed to send email. Please try again."})
    
@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    captcha = data.get('captcha')
    registration_time = datetime.datetime.now()

    try:
        # 查询数据库中是否存在该邮箱
        existing_entry = db_helper.fetch_one("SELECT * FROM verification_codes WHERE BINARY email = %s", (email,))
        
        if existing_entry:
            # 检查用户是否已经注册
            if db_helper.fetch_one("SELECT * FROM users WHERE BINARY username = %s", (username,)):
                return jsonify({"success": "no", "error": "Username already exists. Please try again."})
            # 检查验证码是否正确
            if existing_entry[1] == captcha:
                # 检查验证码是否超时（5分钟）
                captcha_time = existing_entry[2]
                if (registration_time - captcha_time).total_seconds() > 300:
                    return jsonify({"success": "no", "error": "Captcha has expired. Please try again."})
                
                # 插入新用户到数据库中，并将是否被拉黑设置为否
                db_helper.execute_query(
                    "INSERT INTO users (username, email, password, registration_time, is_blacklisted) VALUES (BINARY %s, BINARY %s, BINARY %s, %s, %s)",
                    (username, email, password, registration_time, False)
                )
                return jsonify({"success": "yes"})
            else:
                return jsonify({"success": "no", "error": "Invalid captcha. Please try again."})
        else:
            return jsonify({"success": "no", "error": "Invalid email. Please try again."})
    except Exception as e:
        print(e)
        return jsonify({"success": "no", "error": "Database error. Please try again."})
    
@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    try:
        # 查询数据库中是否存在该用户，区分大小写
        user = db_helper.fetch_one("SELECT * FROM users WHERE BINARY username = %s AND BINARY password = %s", (username, password))
        
        if user:
            if user[4]:
                return jsonify({"success": "no", "error": "You have been blacklisted. Please contact the administrator."})
            else:
                # 生成一个 token（这里简单示例，实际应用中应使用更安全的方法生成 token）
                token = secrets.token_urlsafe(64)

                # 更新数据库中的 token
                db_helper.execute_query(
                    "UPDATE users SET authToken = %s WHERE BINARY username = %s",
                    (token, username)
                )

                # 创建响应对象
                response = make_response(jsonify({"success": "yes", "token": token}))

                # 设置 cookie，过期时间为 7 天
                expires = datetime.datetime.now() + datetime.timedelta(days=7)
                response.set_cookie('authToken', token, expires=expires)

                return response
        else:
            return jsonify({"success": "no", "error": "Invalid username or password. Please try again."})
    except Exception as e:
        return jsonify({"success": "no", "error": "Database error. Please try again."})

@app.route('/api/reset-password', methods=['POST'])
def reset_password():
    data = request.json
    username = data.get('username')
    password = data.get('newPassword')
    captcha = data.get('captcha')
    reset_time = datetime.datetime.now()

    try:
        # 查询数据库中是否存在该用户
        existing_entry = db_helper.fetch_one("SELECT * FROM users WHERE BINARY username = %s", (username,))
        
        if existing_entry:
            # 查询数据库中是否存在该邮箱
            email = existing_entry[2]
            existing_entry = db_helper.fetch_one("SELECT * FROM verification_codes WHERE BINARY email = %s", (email,))
            
            if existing_entry:
                # 检查验证码是否正确
                if existing_entry[1] == captcha:
                    # 检查验证码是否超时（5分钟）
                    captcha_time = existing_entry[2]
                    if (reset_time - captcha_time).total_seconds() > 300:
                        return jsonify({"success": "no", "error": "Captcha has expired. Please try again."})
                    
                    # 更新数据库中该用户的密码
                    db_helper.execute_query(
                        "UPDATE users SET password = %s WHERE BINARY username = %s",
                        (password, username)
                    )
                    return jsonify({"success": "yes"})
                else:
                    return jsonify({"success": "no", "error": "Invalid captcha. Please try again."})
            else:
                return jsonify({"success": "no", "error": "Invalid email. Please try again."})
        else:
            return jsonify({"success": "no", "error": "Invalid username. Please try again."})
    except Exception as e:
        return jsonify({"success": "no", "error": "Database error. Please try again."})

@app.route('/api/verify-token', methods=['POST'])
def verify_token():
    data = request.json
    token = data.get('token')

    try:
        # 查询数据库中是否存在该 token
        user = db_helper.fetch_one("SELECT * FROM users WHERE BINARY authToken = %s", (token,))
        
        if user:
            return jsonify({"success": "yes"})
        else:
            return jsonify({"success": "no", "error": "Invalid token"})
    except Exception as e:
        return jsonify({"success": "no", "error": "Database error. Please try again."})
    
@app.route('/api/get-chat-list', methods=['POST'])
def get_chat_list():
    data = request.json
    token = data.get('token')
    try:
        # 查询数据库中是否存在该 token
        user = db_helper.fetch_one("SELECT username FROM users WHERE BINARY authToken = %s", (token,))
        
        if user:
            username = user[0]
            # 查询数据库中该用户的所有对话数据，并按 generated_at 时间从早到晚排序
            conversations = db_helper.fetch_all("SELECT conversation, sender, message, generated_at FROM conversations WHERE BINARY username = %s ORDER BY generated_at ASC", (username,))
            
            chat_dict = {}
            for conversation, sender, message, generated_at in conversations:
                if conversation not in chat_dict:
                    chat_dict[conversation] = {'conversation': conversation, 'messages': []}
                chat_dict[conversation]['messages'].append({'sender': sender, 'message': message})
            
            chat_list = list(chat_dict.values())
            return jsonify({"success": "yes", "chatList": chat_list})
        else:
            return jsonify({"success": "no", "error": "Invalid token"})
    except Exception as e:
        return jsonify({"success": "no", "error": "Database error. Please try again."})

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    token = data.get('token')
    conversation = data.get('conversation')
    message = data.get('message')

    try:
        # 查询数据库中是否存在该 token
        user = db_helper.fetch_one("SELECT username FROM users WHERE BINARY authToken = %s", (token,))
        
        if user:
            username = user[0]
            #插入新消息到数据库中
            db_helper.execute_query(
                "INSERT INTO conversations (username, conversation, sender, message) VALUES (BINARY %s, %s, %s, %s)",
                (username, conversation, 'user', message,)
            )

            # 查询数据库中该用户的所有对话数据，并按 generated_at 时间从早到晚排序
            conversations = db_helper.fetch_all("SELECT sender, message, generated_at FROM conversations WHERE BINARY username = %s AND conversation = %s ORDER BY generated_at ASC", (username,conversation,))
            messages = []
            for sender, message, generated_at in conversations:
                messages.append({'role': sender, 'content': message})

            # 调用OpenAI接口
            # 初始化OpenAI客户端
            client = OpenAI(
                # 如果没有配置环境变量，请用百炼API Key替换：api_key="sk-xxx"
                api_key = "sk-f4e5a8ed44284e9b95f34f614f70e0bc",
                base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
            )            

            # 创建聊天完成请求
            completion = client.chat.completions.create(
                model="deepseek-r1",  # 此处以 deepseek-r1 为例，可按需更换模型名称
                messages=messages,
                stream=True,
            )

            def generate():

                answer_content = ""     # 定义完整回复
                is_answering = False   # 判断是否结束思考过程并开始回复

                yield f'<small style="color: gray;">' + "***思考过程***" + "</small><br><br>"
                for chunk in completion:
                    # 如果chunk.choices为空，则打印usage
                    if not chunk.choices:
                        continue
                    else:
                        delta = chunk.choices[0].delta
                        # 打印思考过程
                        if hasattr(delta, 'reasoning_content') and delta.reasoning_content != None:
                            yield f'<small style="color: gray;">' + delta.reasoning_content + "</small>"
                        else:
                            # 开始回复
                            if delta.content != "" and is_answering == False:
                                yield f"<br><br>" + "***完整回复***" + "<br><br>"
                                is_answering = True
                            # 打印回复过程
                            yield delta.content
                            answer_content += delta.content
                db_helper.execute_query(
                    "INSERT INTO conversations (username, conversation, sender, message) VALUES (BINARY %s, %s, %s, %s)",
                    (username, conversation, 'assistant', answer_content,)
                )
            return Response(generate(), mimetype='text/plain')
        else:
            return jsonify({"success": "no", "error": "Invalid token"})
    except Exception as e:
        print(e)
        return jsonify({"success": "no", "error": "Database error. Please try again."})

@app.route('/api/delete-chat', methods=['POST'])
def delete_chat():
    data = request.json
    token = data.get('token')
    conversation = data.get('conversation')

    try:
        # 查询数据库中是否存在该 token
        user = db_helper.fetch_one("SELECT username FROM users WHERE BINARY authToken = %s", (token,))
        
        if user:
            username = user[0]
            # 删除数据库中该用户的指定对话数据
            db_helper.execute_query(
                "DELETE FROM conversations WHERE BINARY username = %s AND conversation = %s",
                (username, conversation)
            )
            # 将所有数据库中conversation属性大于客户端回传值的全部减1
            db_helper.execute_query(
                "UPDATE conversations SET conversation = conversation - 1 WHERE BINARY username = %s AND conversation > %s",
                (username, conversation)
            )
            return jsonify({"success": "yes"})
        else:
            return jsonify({"success": "no", "error": "Invalid token"})
    except Exception as e:
        print(e)
        return jsonify({"success": "no", "error": "Database error. Please try again."})


if __name__ == '__main__':
    context = ('ssl/weakcbd.top_bundle.pem','ssl/weakcbd.top.key')
    #app.run(host='::', port=443, ssl_context=context)
    app.run()
