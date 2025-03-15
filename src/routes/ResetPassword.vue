<template>
    <div class="reset-password">
        <h1>重置密码</h1>
        <form @submit.prevent="resetPassword">
            <div class="form-group">
                <label for="username">用户名:</label>
                <input type="text" v-model="username" required />
            </div>
            <div class="form-group captcha-container">
                <label for="captcha">验证码:</label>
                <input type="text" v-model="captcha" required />
                <button type="button" @click="sendCaptcha" :disabled="isCaptchaButtonDisabled">
                    {{ captchaButtonText }}
                </button>
            </div>
            <div class="form-group">
                <label for="newPassword">新密码:</label>
                <input type="password" v-model="newPassword" required />
            </div>
            <button type="submit">重置密码</button>
        </form>
        <transition name="fade">
            <div v-if="showAlert" :class="alertClass">
                {{ alertMessage }}
            </div>
        </transition>
    </div>
</template>

<script>
import axios from 'axios';

export default {
    name: 'ResetPassword',
    data() {
        return {
            username: '',
            captcha: '',
            newPassword: '',
            isCaptchaButtonDisabled: false,
            captchaButtonText: '发送',
            showAlert: false,
            alertMessage: '',
            alertClass: 'alertred',
            countdown: 30,
            api: 'https://weakcbd.top/api'
        };
    },
    methods: {
        resetPassword() {
            // Add your password reset logic here
            console.log('Username:', this.username);
            console.log('Captcha:', this.captcha);
            console.log('New Password:', this.newPassword);
            // Example logic for resetting password
            axios.post(this.api+'/reset-password', {
                username: this.username,
                captcha: this.captcha,
                newPassword: this.newPassword
            })
            .then(response => {
                console.log('Password reset:', response.data);
                if (response.data.success == 'yes') {
                    this.alertClass = 'alertgreen';
                    this.alertMessage = '密码重置成功！';
                    this.showAlert = true;
                    setTimeout(() => {
                        this.showAlert = false;
                        this.$router.push('/UserLogin');
                    }, 1000); // Show alert for 1 second
                } else {
                    this.alertClass = 'alertred';
                    this.alertMessage = response.data.error;
                    this.showAlert = true;
                    setTimeout(() => {
                        this.showAlert = false;
                    }, 1000); // Show alert for 1 second
                }
            })
            .catch(error => {
                console.error('Error resetting password:', error);
                this.alertClass = 'alertred';
                this.alertMessage = '发生错误，请重试。';
                this.showAlert = true;
                setTimeout(() => {
                    this.showAlert = false;
                }, 1000); // Show alert for 1 second
            });
        },
        sendCaptcha() {
            if (!this.username) {
                this.alertClass = 'alertred';
                this.alertMessage = '请填写用户名。';
                this.showAlert = true;
                setTimeout(() => {
                    this.showAlert = false;
                }, 1000); // Show alert for 1 second
                return;
            }

            this.isCaptchaButtonDisabled = true;
            this.captchaButtonText = '发送中...';

            // Send captcha request to the backend
            axios.post(this.api+'/send-captcha', {
                username: this.username,
                type: 'reset-password'
            })
            .then(response => {
                console.log('Captcha sent:', response.data);
                if (response.data.success == 'yes') {
                    this.alertClass = 'alertgreen';
                    this.alertMessage = '验证码发送成功。';
                    this.showAlert = true;
                    setTimeout(() => {
                        this.showAlert = false;
                    }, 1000); // Show alert for 1 second
                    this.startCountdown();
                } else {
                    this.alertClass = 'alertred';
                    this.alertMessage = response.data.error;
                    this.showAlert = true;
                    setTimeout(() => {
                        this.showAlert = false;
                    }, 1000); // Show alert for 1 second
                    this.isCaptchaButtonDisabled = false;
                    this.captchaButtonText = '发送';
                }
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
.reset-password {
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

.reset-password h1 {
    text-align: center;
}

.reset-password form {
    display: flex;
    flex-direction: column;
}

.form-group {
    display: flex;
    align-items: center;
    margin-bottom: 1rem;
}

.form-group label {
    flex: 1;
    margin-right: 10px;
    font-weight: 400;
    text-align: left;
}

.form-group input {
    flex: 2;
    padding: 0.5rem;
    border: 1px solid #ccc;
    border-radius: 4px;
}

.captcha-container {
    display: flex;
    align-items: center;
}

.captcha-container input {
    flex: 2;
}

.reset-password .captcha-container button {
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

.reset-password button {
    padding: 0.5rem;
    border: none;
    border-radius: 4px;
    background-color: #007bff;
    color: white;
    cursor: pointer;
}

.reset-password button:hover {
    background-color: #0056b3;
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