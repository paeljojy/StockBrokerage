<script lang="ts">

import { getStocksFromServer } from '../stocks/StocksAPI.ts'
import { ref } from 'vue';


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
            isUserLoggedIn: false,
            userName: ""
        }
    },
    methods: {
        async fetchStocks() {
        }
    }
}

</script>

<template>
    <div class="portfolio">
        <h1>This is the user portfolio page</h1>
        <button @click="isUserLoggedIn = !isUserLoggedIn">Log in</button>
        <h1 v-if="isUserLoggedIn">Logged in as: {{userName}}</h1>
    </div>
</template>

<style>
@media (min-width: 1024px) {
    .portfolio {
        display: block;
    }
}
</style>
