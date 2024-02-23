<script lang="ts">
import { getStocksFromServer } from '../stocks/StocksAPI.ts'
import { getDB } from '../stocks/StocksAPI.ts'
import { sendLogin } from '../stocks/StocksAPI.ts'
import { sendLogout } from '../stocks/StocksAPI.ts'
import { sendBidAdditionRequest } from '../stocks/StocksAPI.ts'
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
            loginCredential: {},
            amount: 0,
            price: 0,
            // TODO: Query these from the server when we open the stock page
            currentStock: {
                id: 1,
                name: 'Apple, Inc (AAPL)',
                price: 69.69
            }
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
            const loggedOutSuccessFully = await sendLogout(this.loginCredential);
            this.isUserLoggedIn = !loggedOutSuccessFully;
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
        },
        requestBidAddition() {
            const bidData = {
                // INFO: We are not setting the bid id here, 
                // because the server will determine that as the bid is actually being added
                user_id : this.loginCredential.sub,
                stock_id : this.currentStock.id,
                amount : this.amount,
                price : this.price
            };
            console.log("Ord(number) - amount: " + this.amount + " price: @ " + this.price);
            sendBidAdditionRequest(this.loginCredential, bidData);
        },
        requestSellAddition() {
            const sellData = {
              amount: this.amount,
              price: this.price
            };
            console.log("Ord(number) - amount: " + this.amount + " price: @ " + this.price);
        }
    },
    mounted() {
        /* console.log("Google App ID: " + this.googleAppID); */
    }
}
</script>

<template>
    <div class="app-container">
        <div class="stock-container">
            <header>
                <h1>Apple, Inc (AAPL)</h1>
                <div class="price">Loading...</div>
            </header>
            <section class="chart">
                <!-- CHART -->
            </section>
            <div class="trade-controls">
                <div class="input-group">
                    <label for="amount">AMOUNT</label>
                    <input type="number" id="amount" min="0" class="trade-input" v-model.number="amount">
                </div>
                <div class="input-group">
                    <label for="price">PRICE</label>
                    <input type="number" id="price" min="0" class="trade-input" step="0.01" v-model.number="price">
                    <!-- FIXME: Make sure the price input uses two decimals -->
                </div>
                <div class="button-group">
                    <button class="trade-btn bid" @click="requestBidAddition">BID</button>
                    <button class="trade-btn sell" @click="requestSellAddition">SELL</button>
                </div>
            </div>
        </div>
        <div class="stocks">
            <h1>This is the stocks trading page</h1>
            <button @click="fetchStocks">Fetch Stocks</button>
            <button @click="get_database_data_from_server">Fetch Users from DB</button>
            <!-- <button @click="isUserLoggedIn = !isUserLoggedIn">Log in</button> -->
        </div>
        <div>
            <h1 v-if="isUserLoggedIn">Logged in as: {{userName}}</h1>
            <button @click="sendLogoutRequest" v-if="isUserLoggedIn">Log out</button>
            <GoogleLogin :callback="callback" v-if="!isUserLoggedIn"/>
        </div>
        <!-- <div> -->
        <!--     <input type="sendLogInRequest" v-model="email" /> -->
        <!--     <button @click="sendLogInRequest">Log in</button> -->
        <!-- </div> -->
    </div>
</template>

<style>
@media (min-width: 1024px) {
    .stocks {
        display: block;
    }
}

body, html {
  height: 100%;
  margin: 0;
  font-family: 'Arial', sans-serif;
  color: white;
}

.stock-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
  text-align: center;
}

header h1 {
  margin: 0;
  font-size: 24px;
}

.price {
  font-size: 32px;
  font-weight: bold;
  margin: 20px 0;
}

.chart {
  height: 300px;
  background-color: #252547;
  margin-bottom: 20px;
  border-radius: 30px;
}

.trade-controls {
  display: flex;
  flex-direction: column;
  gap: 10px;
  position: relative;
}

.input-group, .button-group {
  position: relative;
}

label {
  position: absolute;
  top: 50%;
  left: 20%;
  transform: translateY(-50%);
  color: #ffffff;
  pointer-events: none;
  font-size: 16px;
}

.trade-input {
  padding: 10px 0px 10px 30px;
  font-size: 16px;
  box-sizing: border-box;
  border-radius: 30px;
}

input::-webkit-outer-spin-button,
      input::-webkit-inner-spin-button {
         -webkit-appearance: none;
      }

.trade-btn {
  flex: 1;
  padding: 20px 100px 20px 100px;
  font-size: 16px;
  cursor: pointer;
  border: none;
  border-radius: 20px;
  margin: 10px 70px;
}


.bid {
  background-color: #4caf50;
  color: white;
}

.sell {
  background-color: #f44336;
  color: white;
}

</style>
