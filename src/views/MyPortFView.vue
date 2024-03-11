<script lang="ts">

import { sendLogin } from '../stocks/StocksAPI.ts'
import { sendLogout } from '../stocks/StocksAPI.ts'
import { decodeCredential } from 'vue3-google-login'
import { getBidsFromServer } from '../stocks/StocksAPI.ts'
import { getTradesFromServer } from '../stocks/StocksAPI.ts'
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
            userName: "",
            email: '',
            // TODO: could wrap user data in an object
            userFirstName: '',
            userLastName: '',
            loginCredential: {},
            userBids: [],
            userSellOffers: [],
            userTrades: [],
        }
    },
    methods: {
        async fetchStocks() {
        },
        async sendLogoutRequest() {
            const loggedOutSuccessFully = true;
                await sendLogout(this.loginCredential);
            if (loggedOutSuccessFully) {
                // Clear localstorage 
                localStorage.removeItem('isLoggedIn');
                localStorage.removeItem('loginCredential');

                this.isUserLoggedIn = false;
            }
        },
        async sendLoginRequest(response) {
            console.log("Logged In!");
            /* console.log(decodeCredential(response.credential)); */
            const credential = decodeCredential(response.credential);
            this.email = credential.email;
            this.userName = credential.name;
            this.loginCredential = credential;
            // Parse first and last name from the response

            console.log("Email: " + this.email);
            console.log("Name: " + this.userName);

            // Use localstorage to save login info
            localStorage.setItem('isLoggedIn', 'true');
            localStorage.setItem('loginCredential', JSON.stringify(credential));

            const ret = sendLogin(this.loginCredential);
            console.log("Send Login responded: " + ret);
            this.isUserLoggedIn = true;
        },
        async fetchUserData() {

        const bids = await getBidsFromServer(this.loginCredential);
        if (bids) {
            this.userBids = bids;
        }

        /* const sellOffers = await getSellOffersFromServer(this.loginCredential);
        if (sellOffers) {
            this.userSellOffers = sellOffers;
        } */

        const trades = await getTradesFromServer(this.loginCredential);
        if (trades) {
            this.userTrades = trades;
        }
        },
        async checkIsUserLoggedIn() {
            const isLoggedIn = localStorage.getItem('isLoggedIn');
            if (isLoggedIn === 'true') {
                const loginCredential = JSON.parse(localStorage.getItem('loginCredential'));
                if (loginCredential) {
                    this.isUserLoggedIn = true;
                    this.email = loginCredential.email;
                    this.userName = loginCredential.name;
                    this.loginCredential = loginCredential;
                } else {
                    console.error('Invalid login credentials');
                }
            }
        },
    },
    mounted() {
        this.checkIsUserLoggedIn();
        
        if (this.isUserLoggedIn) {
            this.fetchUserData();
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
    <div v-if="isUserLoggedIn">
      <hr>
      <h2>User information:</h2>
      <p>Email: {{ email }}</p>
      <p>Name: {{ userName }}</p>
      <hr>
    </div>
    <!-- User bids -->
    <div v-if="isUserLoggedIn && userBids.length > 0">
      <h2>User Bids</h2>
      <ul>
        <li v-for="bid in userBids" :key="bid.id">
          Amount: {{ bid.amount }}      Price: {{ bid.price }}
        </li>
      </ul>
    </div>
    <!-- User sell offers -->
    <div v-if="isUserLoggedIn && userSellOffers.length > 0">
      <h2>User Sell Offers</h2>
      <ul>
        <li v-for="sellOffer in userSellOffers" :key="sellOffer.id">
          Amount: {{ sellOffer.amount }}        Price: {{ sellOffer.price }}
        </li>
      </ul>
    </div>
    <!-- User trades -->
    <div v-if="isUserLoggedIn && userTrades.length > 0">
      <h2>User Trades</h2>
      <ul>
        <li v-for="trade in userTrades" :key="trade.id">
          Amount: {{ trade.amount }}        Price: {{ trade.price }}
        </li>
      </ul>
    </div>
</template>

<style>
@media (min-width: 1024px) {
    .portfolio {
        display: block;
    }
}
</style>
