<script lang="ts">
import { getStocksFromServer } from '../stocks/StocksAPI.ts'
import { getDB } from '../stocks/StocksAPI.ts'
import { sendLogin } from '../stocks/StocksAPI.ts'
import { sendLogout } from '../stocks/StocksAPI.ts'
import { decodeCredential } from 'vue3-google-login'
/*import { ref } from 'vue';*/

/* import { getDB } from '../stocks/Stocks.ts' */

export default {
    data() {
        return {
            stocks: [],
            // This callback will be triggered when the user selects or login to
            // his Google account from the popup
            db: [],
            email: '',
            isUserLoggedIn: false,
            userName: '',
            loginCredential: {}
        }
    },
    methods: {
        async fetchStocks() {
            this.stocks = await getStocksFromServer();
        },
        async get_database_data_from_server() {
            this.db = await getDB();
        },
        async sendLogInRequest() {
            await sendLogin(this.loginCredential);
        },
        async sendLogoutRequest() {
            await sendLogout(this.loginCredential);
            this.isUserLoggedIn = false; 
        },
        async callback(response) {
            console.log("Logged In!");
            /* console.log(decodeCredential(response.credential)); */
            const credential = decodeCredential(response.credential);
            this.email = credential.email;
            this.userName = credential.name;
            this.loginCredential = credential;
            console.log("Email: " + this.email);
            console.log("Name: " + this.userName);

            const tepi = sendLogin(decodeCredential(response.credential));
            console.log(tepi);
            this.isUserLoggedIn = true;
        }
    },
    mounted() {
        /* console.log("Google App ID: " + this.googleAppID); */
    }
}
</script>

<template>
    <div class="stocks">
        <h1>This is the stocks trading page</h1>
        <button @click="fetchStocks">Fetch Stocks</button>
        <button @click="get_database_data_from_server">Create DB</button>
        <!-- <button @click="isUserLoggedIn = !isUserLoggedIn">Log in</button> -->
    </div>
    <!-- FIXME: Some reason doesn't log out user on the backend, "no user found in logged in users" -->
    <div>
        <h1 v-if="isUserLoggedIn">Logged in as: {{userName}}</h1>
        <button v-if="isUserLoggedIn" @click="sendLogoutRequest">Log out</button>
        <GoogleLogin :callback="callback" v-if="!isUserLoggedIn"/>
    </div>
    <!-- <div> -->
    <!--     <input type="sendLogInRequest" v-model="email" /> -->
    <!--     <button @click="sendLogInRequest">Log in</button> -->
    <!-- </div> -->
</template>

<style>
@media (min-width: 1024px) {
    .stocks {
        display: block;
    }
}
</style>
