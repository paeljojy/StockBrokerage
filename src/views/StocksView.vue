<script lang="ts">
import { getStocks } from '../stocks/Stocks.ts'
import { getDB } from '../stocks/Stocks.ts'
import { decodeCredential } from 'vue3-google-login'

/* import { getDB } from '../stocks/Stocks.ts' */

export default {
    data() {
        return {
            stocks: [],
            // This callback will be triggered when the user selects or login to
            // his Google account from the popup
            callback: (response) => {
                console.log("Logged In!");
                console.log(decodeCredential(response.credential));
            },
            db: []
        }
    },
    methods: {
        async fetchStocks() {
            this.stocks = await getStocks();
        },
        /* , */
        /* async createDb() { */
        /*     console.log("Creating DB"); */
        /*     this.db = await getDB(); */
        /* } */
        async getDB() {
            this.db = await getDB();
        }
    }
}

</script>

<template>
    <div class="stocks">
        <h1>This is the stocks trading page</h1>
        <button @click="fetchStocks">Fetch Stocks</button>
        <button @click="getDB">Create DB</button>
    </div>
    <GoogleLogin :callback="callback" />
</template>

<style>
@media (min-width: 1024px) {
    .stocks {
        display: block;
    }
}
</style>
