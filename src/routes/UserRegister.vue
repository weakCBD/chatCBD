<template>
    <div class="register">
        <h1>注册</h1>
        <form @submit.prevent="register">
            <div>
                <label for="username">用户名:</label>
                <input type="text" id="username" v-model="username" required />
            </div>
            <div>
                <label for="email">邮箱:</label>
                <input type="email" id="email" v-model="email" required />   
            </div>
            <div class="captcha-container">
                <label for="captcha">验证码:</label>
                <input type="text" id="captcha" v-model="captcha" required />
                <button type="button" @click="sendCaptcha" :disabled="isCaptchaButtonDisabled">
                    {{ captchaButtonText }}
                </button>
            </div>
            <div>
                <label for="password">密码:</label>
                <input type="password" id="password" v-model="password" required />
            </div>
            <button type="submit" :disabled="isRegisterButtonDisabled">{{RegisterText}}</button>
        </form>
        <transition name="fade">
            <div v-if="showAlert" :class="alertclass">
                {{ alertMessage }}
            </div>
        </transition>
    </div>
</template>

<script>
import axios from 'axios';

export default {
    name: 'UserRegister',
    data() {
        return {
            username: '',
            email: '',
            password: '',
            captcha: '',
            isCaptchaButtonDisabled: false,
            captchaButtonText: '发送',
            isRegisterButtonDisabled: false,
            RegisterText: '注册',
            showAlert: false,
            countdown: 30,
            alertclass: 'alertred',
            alertMessage: '请输入您的邮箱。',
            api: 'https://weakcbd.top/api'
        };
    },
    methods: {
        register() {
            // Handle registration logic here
            console.log('注册:', this.username, this.email, this.password);
            console.log('验证码:', this.captcha);
            if(this.username.length > 60 && this.email.length > 60 && this.password.length > 60 && this.captcha.length > 6){
                this.showAlert = true;
                this.alertclass = 'alertred';
                this.alertMessage = '输入超过长度限制。';
                setTimeout(() => {
                    this.showAlert = false;
                }, 1000); // Show alert for 1 seconds
                return;
            }

            this.isRegisterButtonDisabled = true;
            this.RegisterText = '注册中...';

            axios.post(this.api+'/register', {
                username: this.username,
                password: this.password,
                email: this.email,
                captcha: this.captcha
            })
            .then(response => {
                console.log('Register', response.data);
                if(response.data.success == 'yes'){
                    this.showAlert = true;
                    this.alertclass = 'alertgreen';
                    this.alertMessage = '注册成功。1秒后自动跳转。';
                    setTimeout(() => {
                        this.showAlert = false;
                        this.$router.push('/UserLogin');
                        this.isRegisterButtonDisabled = false;
                        this.RegisterText = '注册';
                    }, 1000); // Show alert for 1 seconds
                    this.startCountdown();
                }else if(response.data.success == 'no'){
                    this.showAlert = true;
                    this.alertclass = 'alertred';
                    this.alertMessage = response.data.error;
                    setTimeout(() => {
                        this.showAlert = false;
                    }, 1000); // Show alert for 1 seconds
                    this.isRegisterButtonDisabled = false;
                    this.RegisterText = '注册';
                }
                
            })
            .catch(error => {
                console.error('Error register:', error);
                this.alertClass = 'alertred';
                this.alertMessage = '发生错误，请重试。';
                this.showAlert = true;
                setTimeout(() => {
                    this.showAlert = false;
                }, 1000); // Show alert for 1 second
                this.isRegisterButtonDisabled = false;
                this.RegisterText = '注册';
            });
        },
        sendCaptcha() {
            if (!this.email) {
                this.showAlert = true;
                this.alertclass = 'alertred';
                this.alertMessage = '请输入您的邮箱。';
                setTimeout(() => {
                    this.showAlert = false;
                }, 1000); // Show alert for 1 seconds
                return;
            }

            // Validate email format
            const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailPattern.test(this.email)) {
                this.showAlert = true;
                this.alertclass = 'alertred';
                this.alertMessage = '请输入有效的邮箱地址。';
                setTimeout(() => {
                    this.showAlert = false;
                }, 1000); // Show alert for 1 seconds
                return;
            }

            this.isCaptchaButtonDisabled = true;
            this.captchaButtonText = '发送中...';

            // Send captcha request to the backend
            axios.post(this.api+'/send-captcha', {
                username: this.username,
                email: this.email,
                type: 'register'
            })
            .then(response => {
                console.log('Captcha sent:', response.data);
                if(response.data.success == 'yes'){
                    this.showAlert = true;
                    this.alertclass = 'alertgreen';
                    this.alertMessage = '验证码发送成功。';
                    setTimeout(() => {
                        this.showAlert = false;
                    }, 1000); // Show alert for 1 seconds
                    this.startCountdown();
                }else if(response.data.success == 'no'){
                    this.showAlert = true;
                    this.alertclass = 'alertred';
                    this.alertMessage = response.data.error;
                    setTimeout(() => {
                        this.showAlert = false;
                    }, 1000); // Show alert for 1 seconds
                }
                this.isCaptchaButtonDisabled = false;
                this.captchaButtonText = '发送';
            })
            .catch(error => {
                console.error('Error sending captcha:', error);
                this.alertClass = 'alertred';
                this.alertMessage = '发生错误，请重试。';
                this.showAlert = true;
                setTimeout(() => {
                    this.showAlert = false;
                }, 1000); // Show alert for 1 second
                this.isCaptchaButtonDisabled = false;
                this.captchaButtonText = '发送';
            });
            
        },
        startCountdown() {
            this.countdown = 30;
            this.captchaButtonText = `${this.countdown}s`;
            const interval = setInterval(() => {
                this.countdown -= 1;
                this.captchaButtonText = `${this.countdown}s`;
                if (this.countdown <= 0) {
                    clearInterval(interval);
                    this.isCaptchaButtonDisabled = false;
                    this.captchaButtonText = '发送';
                }
            }, 1000);
        }
    }
};
</script>

<style scoped>
.register {
    width: 360px;
    margin: 0 auto;
    padding: 1em;
    border: 1px solid #ccc;
    border-radius: 4px;
    background-color: white; /* 纯白色背景 */
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
}
.register h1 {
    text-align: center;
}
.register div {
    margin-bottom: 15px;
}
.register label {
    display: block;
    margin-bottom: 5px;
}
.register input {
    width: 100%;
    padding: 8px;
    box-sizing: border-box;
}
.register button {
    width: 100%;
    padding: 10px;
    background-color: #007bff;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
}
.register button:hover {
    background-color: #0056b3;
}
.captcha-container {
    display: flex;
    align-items: center;
}
.captcha-container input {
    flex: 2;
}
.captcha-container button {
    flex: 1;
    margin-left: 10px;
    padding: 8px;
    background-color: #28a745;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
}
.captcha-container button:disabled {
    background-color: #6c757d;
    cursor: not-allowed;
}
.captcha-container button:hover:enabled {
    background-color: #218838;
}
.alertred {
    position: fixed;
    top: 0;
    left: 50%;
    transform: translateX(-50%);
    background-color: #f8d7da;
    color: #721c24;
    padding: 10px 20px;
    border: 1px solid #f5c6cb;
    border-radius: 4px;
    z-index: 1000;
    max-width: 400px;
    width: 100%;
    text-align: center;
}
.alertgreen {
    position: fixed;
    top: 0;
    left: 50%;
    transform: translateX(-50%);
    background-color: #c0fd92;
    color: #5eb803;
    padding: 10px 20px;
    border: 1px solid #acff7f;
    border-radius: 4px;
    z-index: 1000;
    max-width: 400px;
    width: 100%;
    text-align: center;
}
.fade-enter-active, .fade-leave-active {
    transition: opacity 0.5s;
}
.fade-enter, .fade-leave-to {
    opacity: 0;
}
</style>