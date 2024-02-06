import './assets/main.css'

import { createApp } from 'vue'
import { createPinia } from 'pinia'
import vue3GoogleLogin from 'vue3-google-login'

import '@fortawesome/fontawesome-free/js/all'

import App from './App.vue'
import router from './router'

const app = createApp(App)

app.use(createPinia())
app.use(router)
app.use(vue3GoogleLogin, {
  clientId: '762542509883-bpcc2b746q0e4blrhodofd20t3p6tvlp.apps.googleusercontent.com'
})

app.mount('#app')
