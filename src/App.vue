<template>
  <div id="app">
    <!-- <nav>
      <router-link to="/">HomePage</router-link> |
      <router-link to="/UserLogin">UserLogin</router-link> |
      <router-link to="/UserRegister">UserRegister</router-link>
    </nav> -->
    <router-view></router-view>
  </div>
</template>

<script>
//import HelloWorld from './components/HelloWorld.vue'

export default {
  name: 'App',
  components: {
    //HelloWorld
  }
}
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  height:100%;
}
</style>
