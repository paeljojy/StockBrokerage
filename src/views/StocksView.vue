<script lang="ts">
import { getStocksFromServer } from '../stocks/StocksAPI.ts'
import { getDB } from '../stocks/StocksAPI.ts'
import { sendLogin } from '../stocks/StocksAPI.ts'
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
            userName: ''
        }
    },
    methods: {
        async fetchStocks() {
            this.stocks = await getStocksFromServer();
        },
        async get_database_data_from_server() {
            this.db = await getDB();
        },
        async submit() {
            await sendLogin(this.email);
        },
        async callback(response) {
            console.log("Logged In!");
            /* console.log(decodeCredential(response.credential)); */
            const credential = decodeCredential(response.credential);
            this.email = credential.email;
            this.userName = credential.name;
            console.log("Email: " + this.email);
            console.log("Name: " + this.userName);

            sendLogin(decodeCredential(response.credential));
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

        <button @click="isUserLoggedIn = !isUserLoggedIn">Log in</button>
        <h1 v-if="isUserLoggedIn">Logged in as: {{userName}}</h1>
    </div>
    <GoogleLogin :callback="callback" />
    <div>
        <input type="email" v-model="email" />
        <button @click="submit">Submit</button>
    </div>
</template>

<style>
@media (min-width: 1024px) {
    .stocks {
        display: block;
    }
}
</style>
