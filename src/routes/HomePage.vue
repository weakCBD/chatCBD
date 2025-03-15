<template>
    <el-container :class="'homepage ' + (elselected ? ' elselected' : ' elunselected')">
        <el-aside class="elAsideClass">
            <div class="logoutcontainer">
                <el-button color="#626aef" plain @click="logOut" class="log-out">登出</el-button>
            </div>
            <el-menu :default-active="activeChat" @select="handleSelect">
                <el-menu-item v-for="(chat, index) in reversedChatList" :key="index" :index="(chatList.length - 1 - index).toString()">
                    <span>{{ chat.messages[0].message }}</span>
                    <el-icon class="delete-icon" @click.stop="deleteChat(chat.conversation, (chatList.length - 1 - index).toString())">
                        <Delete />
                    </el-icon>
                </el-menu-item>
            </el-menu>
        </el-aside>
        <el-container class="elContainerClass">
            <el-main class="main">
                <div class="mask" v-show="elselected" @click="showChatList"></div>
                <div class="welcome" v-show="chatList[activeChat].messages[0].sender === 'none'">
                    <img src="../assets/logo.png" alt="ChatCBD Logo" />
                    <h1>你好，我是ChatCBD</h1>
                    <p>请发送消息与我对话吧</p>
                </div>
                <div class="main-header">
                    <div class="chat-list"  @click="showChatList">
                        <el-icon color="white" size="40"><ChatLineRound /></el-icon>
                    </div>
                    <div class="chat-new"  @click="newChat">
                        <el-icon color="white" size="40"><CirclePlus /></el-icon>
                    </div>
                </div>
                <div class="chat-container" @scroll="onChatContainerScroll">
                    <div class="messages">
                        <div v-for="(message, index) in chatList[activeChat].messages" :key="index">
                            <div v-if="message.sender === 'user'" class="user">
                                <div class="message">
                                    {{ message.message }}
                                </div>
                            </div>
                            <div v-else-if="message.sender === 'assistant'" class="assistant">
                                <div class="sender-avatar">
                                    <el-avatar><img src="../assets/logo.png" alt="ChatCBD Logo" /></el-avatar>
                                    <p>chatCBD</p>
                                </div>
                                <div class="message">
                                    <Markdown :source="message.message" :html="true"/>
                                </div>
                            </div>
                        </div>
                        <div class="scroll-bottom" @click="notreading" v-show="isReading">
                            <el-icon size="40"><ArrowDownBold /></el-icon>
                        </div>
                    </div>
                </div>
                <div class="type-message">
                    <el-input class="message-box" v-model="newMessage" @keyup.enter="sendMessage" placeholder="给chatCBD发送消息" type="textarea" resize="none" :rows="3"/>
                    <div>
                        <el-button class="send-button" color="#626aef" @click="sendMessage" :loading="isgetting">{{sendstatu}}</el-button>
                    </div>
                </div>
            </el-main>
        </el-container>
    </el-container>
</template>

<script>
import axios from 'axios';
import Cookies from 'js-cookie';
import { ElContainer, ElAside, ElMenu, ElMenuItem, ElMain, ElInput, ElButton, ElAvatar} from 'element-plus';
import Markdown from 'vue3-markdown-it';

export default {
    name: 'HomePage',
    components: {
        ElContainer,
        ElAside,
        ElMenu,
        ElMenuItem,
        ElMain,
        ElInput,
        ElButton,
        ElAvatar,
        Markdown
    },
    data() {
        return {
            chatList: [{ conversation: '0', messages: [{sender:'none',message:''}] }],
            newMessage: '',
            activeChat: '0',
            api: 'https://weakcbd.top/api',
            elselected: false,
            isgetting: false,
            sendstatu: '发送',
            isReading: false,
        };
    },
    computed: {
        reversedChatList() {
            return this.chatList.slice().reverse();
        }
    },
    methods: {
        handleSelect(index) {
            this.activeChat = index;
            this.elselected = false;
            this.scrollToBottom();
        },
        sendMessage() {
            this.isgetting=true;
            this.sendstatu='发送中';
            if (this.newMessage.trim() === '') {
                this.isgetting=false;
                this.sendstatu='发送';
                return;
            }
            const authToken = Cookies.get('authToken');
            if (!authToken) {
                this.isgetting=false;
                this.sendstatu='发送';
                this.$router.push('/UserLogin');
                return;
            }

            const message = {
                sender: 'user',
                message: this.newMessage             
            };
            this.chatList[this.activeChat].messages.push(message);
            if(this.chatList[this.activeChat].messages[0].sender === 'none') {
                this.chatList[this.activeChat].messages.shift();
            }
            this.scrollToBottom();
            this.newMessage = '';

            this.isgetting=true;
            this.sendstatu='响应中';

            fetch(this.api + '/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    token: authToken,
                    conversation: this.activeChat.toString(),
                    message: message.message
                })
            })
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Network response was not ok');
                    }
                    const reader = response.body.getReader();
                    const decoder = new TextDecoder('utf-8');
                    const botMessage = {
                        sender: 'assistant',
                        message: ``
                    };
                    this.chatList[this.activeChat].messages.push(botMessage);

                    const readStream = () => {
                        reader.read().then(({ done, value }) => {
                            if (done) {
                                this.isgetting=false;
                                this.sendstatu='发送';
                                return;
                            }
                            const chunk = decoder.decode(value, { stream: true });
                            if(chunk === '{"error":"invalid token","success":"no"}') {
                                this.$router.push('/UserLogin');
                                this.isgetting=false;
                                this.sendstatu='发送';
                                return;
                            }
                            this.chatList[this.activeChat].messages[this.chatList[this.activeChat].messages.length - 1].message += chunk;
                            this.scrollToBottom();
                            readStream();
                        }).catch(err => {
                            this.isgetting=false;
                            this.sendstatu='发送';
                            this.chatList[this.activeChat].messages[this.chatList[this.activeChat].messages.length - 1].message += "服务器繁忙，请稍后再试";
                            this.scrollToBottom();
                            console.error(err);
                        });
                    };
                    readStream();
                })
                .catch(error => {
                    this.isgetting=false;
                    this.sendstatu='发送';
                    console.error('Error:', error);
                });
        },
        checkAuthToken() {
            const authToken = Cookies.get('authToken');
            if (!authToken) {
                this.$router.push('/UserLogin');
                return;
            }

            axios.post(this.api + '/verify-token', { token: authToken })
                .then(response => {
                    if (response.data.success !== 'yes') {
                        this.$router.push('/UserLogin');
                    }
                })
                .catch(() => {
                    this.$router.push('/UserLogin');
                });
        },
        showChatList() {
            if(this.isgetting) return;
            this.elselected = !this.elselected;
        },
        newChat() {
            if(this.isgetting) return;
            if(this.chatList[this.chatList.length - 1].messages[0].sender === 'none') return;
            this.chatList.push({ conversation: this.chatList.length.toString(), messages: [{sender:'none',message:''}] });
            this.activeChat = (this.chatList.length - 1).toString();
            this.elselected = false;
            this.scrollToBottom();
        },
        initializeChat() {
            const authToken = Cookies.get('authToken');
            if (!authToken) {
                this.$router.push('/UserLogin');
                return;
            }
            axios.post(this.api + '/get-chat-list', { token: authToken })
                .then(response => {
                    if(response.data.success !== 'yes') {
                        this.$router.push('/UserLogin');
                        return;
                    }
                    this.chatList = response.data.chatList;
                    if (this.chatList.length === 0) {
                        this.chatList.push({ conversation: '0', messages: [{sender:'none',message:''}] });
                    }
                    this.activeChat = (this.chatList.length - 1).toString();
                    this.scrollToBottom();
                })
                .catch(error => {
                    console.error('Error:', error);
                    this.chatList.push({ conversation: '0', messages: [{sender:'none',message:''}] });
                    this.activeChat = (this.chatList.length - 1).toString();
                    this.scrollToBottom(); // 添加此行
                });
        },
        scrollToBottom() {
            console.log('Scrolling to bottom');
            if(this.isReading) return;
            this.$nextTick(() => {
                const chatContainer = this.$el.querySelector('.chat-container');
                if (chatContainer) {
                    chatContainer.scrollTop = chatContainer.scrollHeight;
                }
                this.isReading = false;
            });
            this.isReading = false;
        },
        deleteChat(conversation, index) {
            const authToken = Cookies.get('authToken');
            if (!authToken) {
                this.$router.push('/UserLogin');
                return;
            }
            if(this.chatList.length === 1){
                return;
            }
            
            axios.post(this.api + '/delete-chat', {
                token: authToken,
                conversation: conversation
            })
            .then(response => {
                if (response.data.success === 'yes') {
                    this.chatList.splice( Number(index), 1);
                    if (this.activeChat === index) {
                        this.activeChat = ( Number(index) - 1).toString();
                    }
                } else {
                    console.error('Failed to delete chat:', response.data.error);
                }
            })
            .catch(error => {
                console.error('Error:', error);
            });
        },
        logOut() {
            Cookies.remove('authToken');
            this.$router.push('/UserLogin');
        },
        onChatContainerScroll() {
            // 滚动事件逻辑
            const chatContainer = this.$el.querySelector('.chat-container');
                if (chatContainer) {
                    if(chatContainer.scrollTop + chatContainer.clientHeight >= chatContainer.scrollHeight-10){
                        this.isReading = false;
                    }else{
                        this.isReading = true;
                    }
                }
        },
        notreading(){
            console.log('not reading');
            this.isReading = false;
            this.scrollToBottom();
            this.isReading = false;
        }
    },
    created() {
        this.checkAuthToken();
        this.initializeChat();
        this.activeChat = (this.chatList.length - 1).toString();
    },
    mounted() {
        window.copyCode = function(button) {
            const code = button.nextElementSibling.innerText;
            navigator.clipboard.writeText(code).then(() => {
                button.innerText = '已复制';
                setTimeout(() => {
                    button.innerText = '复制';
                }, 2000);
            });
        };
    }
};
</script>

<style scoped>
.homepage {
    display:flex;
    height:100%;
    width:167%;
}
.elunselected{
    transform: translate(-40%, 0);
    transition-property: transform;
    transition-duration: 0.5s;
}
.elselected{
    transform: translate(0, 0);
    transition-property: transform;
    transition-duration: 0.5s;
}
.elAsideClass{
    height:100%;
    width:40%;
    background-color: rgb(235, 235, 235);
}
.elAsideClass span{
    max-width: calc(100% - 40px);
    overflow: hidden;
    text-overflow: ellipsis;
}
.elAsideClass li{
    justify-content: space-between;
}
.elContainerClass{
    display: flex;
    height:100%;
    width:60%;
    position:relative;
}
.logoutcontainer{
    display: flex;
    justify-content: flex-end;
    padding: 10px;
    background-color: #959aee;
}
.mask{
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-color: rgba(0, 0, 0, 0.5);
    z-index: 100;
}
.welcome{
    position:absolute;
    width:100%;
    top:40%;
    left:50%;
    transform: translate(-50%, -50%);
    text-align:center;
    color:aliceblue;
}
.welcome img {
    width: 100px; /* Adjust the width as needed */
    height: auto; /* Maintain aspect ratio */
}
.main-header{
    display: flex;
    justify-content: space-between;
    color: white;
    padding: 1em;
}
.chat-list:hover{
    cursor: pointer;
}
.chat-new:hover{
    cursor: pointer;
}
.chat-container{
    display: flex;
    flex-direction: column;
    height: 70%; /* Adjust height to account for header */
    overflow: auto; /* Add overflow to handle content overflow */
    margin-bottom: 1em;
    flex:1;
}

.user{
    display: flex;
    margin: 0.5em;
    flex-direction: column;
    align-items: end;
}

.assistant{
    display: flex;
    flex-direction: column;
    margin: 0.5em;
    align-items: start;
}

.assistant .sender-avatar{
    display: flex;
    align-items: center;
}

.messages .sender-avatar p{
    margin:auto 10px;
    color:aliceblue;
    font-size:1.2em;
}

.messages .message{
    color: rgb(0, 0, 0);
    padding: 10px;
    border-radius: 10px;
    margin-top: 10px;
    text-align: left;
}

.user .message{
    background-color: #626aef;
    color:#f5f5f5;
    max-width: calc(100% - 20px);
}

.user .message > * {
    max-width: 100%;
}

.assistant .message {
  font-family: Arial, sans-serif;
  background-color: rgb(255, 255, 255);
  display: flex;
  flex-wrap: wrap;
  flex-direction: column;
  font-size: 0.9em;
  max-width: calc(100% - 20px);
}

.assistant .message > * {
    max-width: 100%;
}

.main{
    display: flex;
    flex-direction: column;
    height:100%;
    width:100%;
}

.type-message{
    display: flex;
    flex-direction: column;
}

.send-button{
    margin-top:8px;
    height:40px;
    width:140px;
    float: right;
}

.delete-icon {
    float: right;
    cursor: pointer;
}

pre {
    background-color: #272822 !important; /* Monokai Sublime 背景色 */
    position: relative;
    padding-top: 30px !important;
}
  
code {
    background-color: #272822 !important; /* Monokai Sublime 背景色 */
    color: #f8f8f2 !important; /* Monokai Sublime 代码颜色 */
}

.copy-btn {
    position: absolute;
    right: 10px;
    top: 5px;
    padding: 5px 10px;
    background: #555;
    border: none;
    color: white;
    cursor: pointer;
    border-radius: 3px;
}

.copy-btn:hover {
    background: #666;
}

.scroll-bottom{
    position:absolute;
    padding:5px;
    bottom:155px;
    left:50%;
    transform: translate(-50%, 0);
    cursor: pointer;
    margin-bottom: 10px;
    border-radius: 50%;
    color: white;
    background-color: #959aee;
    box-shadow: 0 4px 8px rgba(0, 0, 0,0.9); /* 添加阴影 */
}
</style>