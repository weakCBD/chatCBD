<template>
    <div class="login">
        <h1>登录</h1>
        <form @submit.prevent="handleLogin">
            <div>
                <label for="username">用户名:</label>
                <input type="text" v-model="username" id="username" required />
            </div>
            <div>
                <label for="password">密码:</label>
                <input type="password" v-model="password" id="password" required />
            </div>
            <button type="submit" :disabled="isLoginButtonDisabled">{{LoginText}}</button>
        </form>
        <router-link to="/UserRegister" class="register-link">没有账号？点击注册</router-link>
        <button @click="forgotPassword" class="forgot-password-button">忘记密码？</button>
        <transition name="fade">
            <div v-if="showAlert" :class="alertClass">
                {{ alertMessage }}
            </div>
        </transition>
    </div>
</template>

<script>
import axios from 'axios';
import Cookies from 'js-cookie';

export default {
    name: 'UserLogin',
    data() {
        return {
            username: '',
            password: '',
            showAlert: false,
            alertMessage: '',
            alertClass: 'alertred',
            isLoginButtonDisabled: false,
            LoginText: '登录',
            api: 'https://weakcbd.top/api'
        };
    },
    methods: {
        handleLogin() {
            this.isLoginButtonDisabled = true;
            this.LoginText = '登录中...';
            // Handle login logic here
            axios.post(this.api+'/login', {
                username: this.username,
                password: this.password
            })
            .then(response => {
                if (response.data.success == 'yes') {
                    // Set cookies
                    Cookies.set('authToken', response.data.token, { expires: 7 }); // 7 days expiration
                    this.alertClass = 'alertgreen';
                    this.alertMessage = '登录成功！';
                    this.showAlert = true;
                    setTimeout(() => {
                        this.showAlert = false;
                        this.$router.push('/Chat');
                    }, 1000); // Show alert for 1 second
                } else {
                    this.alertClass = 'alertred';
                    this.alertMessage = response.data.error;
                    this.showAlert = true;
                    setTimeout(() => {
                        this.showAlert = false;
                    }, 1000); // Show alert for 1 second
                }
                this.isLoginButtonDisabled = false;
                this.LoginText = '登录';
            })
            .catch(error => {
                console.log(error);
                this.alertClass = 'alertred';
                this.alertMessage = '发生错误，请重试。';
                this.showAlert = true;
                setTimeout(() => {
                    this.showAlert = false;
                }, 1000); // Show alert for 1 second
                this.isLoginButtonDisabled = false;
                this.LoginText = '登录';
            });
        },
        forgotPassword() {
            // Redirect to ResetPassword page
            this.$router.push('/ResetPassword');
        }
    }
};
</script>

<style scoped>
.login {
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
.login h1 {
    text-align: center;
}
.login div {
    margin-bottom: 1em;
}
.login label {
    display: block;
    margin-bottom: 0.5em;
}
.login input {
    width: 100%;
    padding: 0.5em;
    box-sizing: border-box;
}
.login button {
    width: 100%;
    padding: 0.5em;
    background-color: #007BFF;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
}
.login button:hover {
    background-color: #0056b3;
}
.register-link {
    display: block;
    text-align: center;
    margin-top: 1em;
    color: #007BFF;
    text-decoration: none;
}
.register-link:hover {
    text-decoration: underline;
}
.login .forgot-password-button {
    display: block;
    width: 100%;
    padding: 0.5em;
    background-color: #ffc107;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    margin-top: 1em;
}
.login .forgot-password-button:hover {
    background-color: #e0a800;
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