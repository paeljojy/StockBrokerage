<script lang="ts">
import { getStocksFromServer } from '../stocks/StocksAPI'
import { getLastTradedPriceForStock } from '../stocks/StocksAPI'
import { getDB } from '../stocks/StocksAPI'
import { getBidsFromServer } from '../stocks/StocksAPI'
import { sendLogin } from '../stocks/StocksAPI'
import { sendLogout } from '../stocks/StocksAPI'
import { sendBidAdditionRequest } from '../stocks/StocksAPI'
import { sendSellAdditionRequest } from '../stocks/StocksAPI'
import { decodeCredential } from 'vue3-google-login'
import { isProxy, toRaw } from 'vue';

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
            // TODO: could wrap user data in an object
            userFirstName: '',
            userLastName: '',
            loginCredential: {},
            amount: 0,
            price: 0,
            bidDataList: [] as {
                id: number;
                user_id: number;
                stock_id: number;
                amount: number;
                price: number;
                date: string;
            }[],
            sellDataList: [] as {
                id: number;
                user_id: number;
                stock_id: number;
                amount: number;
                price: number;
                date: string;
            }[],
            // TODO: Query these from the server when we open the stock page
            currentStock: {
                id: 1,
                name: 'Apple, Inc (AAPL)',
                price: 0,
                fetched_time: new Date()
            }
        }
    },
    methods: {
        async fetchStocks() {
            // print bid data list
            console.log(this.bidDataList);
        },
        async fetchLastTradedPrice() {
            const newCurrentStock = await getLastTradedPriceForStock(this.loginCredential, this.currentStock.id);
            this.currentStock.price = newCurrentStock.price;
            this.currentStock.fetched_time = newCurrentStock.fetched_time;
            this.currentStock.name = newCurrentStock.name;
            this.currentStock.id = newCurrentStock.id;

            console.log("Last price is: " + this.currentStock.price);
            console.log("Current stock is: " + this.currentStock.name);
            console.log("Current stock id is: " + this.currentStock.id);
            console.log("Fetched time is: " + this.currentStock.fetched_time);
        },
        async get_database_data_from_server() {
            this.db = await getDB();
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
            // FIXME: Only on succesfull login the above code is not tested: test and verify
            this.fetchLastTradedPrice();

            console.log("Send Login responded: " + ret);
            this.isUserLoggedIn = true;

            this.requestBids();
        },
        formatPrice() {
            this.price = parseFloat(this.price.toFixed(2)); // Rounds to nearest (up to) 2 decimals
        },
        async requestBids() {
            try {
                const data = await getBidsFromServer(this.loginCredential);
                this.bidDataList = data[0];
                this.sellDataList = data[1];
                console.log("User bids:", this.bidDataList);
                console.log("User offers:", this.sellDataList);
            } catch (error) {
                console.error("Error fetching bids:", error);
            }
        },
        async requestBidAddition() {
            // INFO: We are not setting the bid id here, 
            // because the server will determine that as the bid is actually being added

            // FIXME: This is actually super dumb that we are sending the date from the client
            // We should be getting the date from the server
            let date = new Date();
            let milliseconds = date.getMilliseconds();
            let dateString = date.toLocaleDateString('en-GB', {
                year: 'numeric',
                month: '2-digit',
                day: '2-digit',
            }) + ' ' + date.toLocaleTimeString('en-GB', {
                hour12: false,
                hour: '2-digit',
                minute: '2-digit',
                second: '2-digit'
            }) + '.' + milliseconds.toString().padStart(3, '0'); // Add ms manually as date doesn't support it out of the box

            const newBidData = {
                user_id: this.loginCredential.sub,
                stock_id: this.currentStock.id,
                amount: this.amount,
                price: this.price,
                date: dateString 
            };

            console.log("Ord(number) - amount: " + this.amount + " price: @ " + this.price);

            const response = await sendBidAdditionRequest(this.loginCredential, newBidData);
            this.requestBids();
        },
        async requestSellAddition() {
            // FIXME: This is actually super dumb that we are sending the date from the client
            // We should be getting the date from the server
            let date = new Date();
            let milliseconds = date.getMilliseconds();
            let dateString = date.toLocaleDateString('en-GB', {
                year: 'numeric',
                month: '2-digit',
                day: '2-digit',
            }) + ' ' + date.toLocaleTimeString('en-GB', {
                hour12: false,
                hour: '2-digit',
                minute: '2-digit',
                second: '2-digit'
            }) + '.' + milliseconds.toString().padStart(3, '0'); // Add ms manually as date doesn't support it out of the box
            const newSellData = {
                user_id: this.loginCredential.sub,
                stock_id: this.currentStock.id,
                amount: this.amount,
                price: this.price,
                date: dateString
            };

            console.log("Ord(number) - amount: " + this.amount + " price: @ " + this.price);
            const response = await sendSellAdditionRequest(this.loginCredential, newSellData);
            this.requestBids();
        }
    },
    mounted() {
        // FIXME: Ask server if the user is logged in
        // this doesn't work atm as the promise returned by this function is not awaited?
        sendLogin(this.loginCredential).then(temp => console.log("")).then(value => this.isUserLoggedIn = value);
        if (this.isUserLoggedIn)
        {
            const bids = getBidsFromServer(this.loginCredential);
            for (let bid in bids)
            {
                this.bidDataList.push(bid);
            }
            /* console.log("Google App ID: " + this.googleAppID); */
        }
        /* console.log("Google App ID: " + this.googleAppID); */

        // Check if the user is logged in
        const isLoggedIn = localStorage.getItem('isLoggedIn') === 'true';
        if (isLoggedIn) {
            this.isUserLoggedIn = true;
            this.loginCredential = JSON.parse(localStorage.getItem('loginCredential') || '{}');
        }
    }
}
</script>

<template>
    <div class="app-container">
        <div class="stock-container">
            <header>
                <h1>Apple, Inc (AAPL)</h1>
                <div class="price"> {{currentStock.price[0]}} USD</div>
            </header>
            <section class="chart">
                <!-- CHART -->
            </section>
            <div class="trade-controls" v-if="isUserLoggedIn">
                <div class="input-group">
                    <label for="amount">AMOUNT</label>
                    <input type="number" id="amount" min="0" class="trade-input" v-model.number="amount">
                </div>
                <div class="input-group">
                    <label for="price">PRICE</label>
                    <input type="number" id="price" min="0" class="trade-input" step="0.01" v-model.number="price" @blur="formatPrice">
                </div>
                <div class="button-group">
                    <button class="trade-btn bid" @click="requestBidAddition">BID</button>
                    <button class="trade-btn sell" @click="requestSellAddition">SELL</button>
                </div>
            </div>
            <div class="Bids-Sells" v-if="isUserLoggedIn">
                <h2>Bids</h2>
                <table class="Bids">
                    <tr>
                        <th>Date</th>
                        <th>Amount</th>
                        <th>Price</th>
                        <th>Action</th>
                    </tr>
                    <tr v-for="(bid, index) in bidDataList" :key="index">
                        <td>{{ bid[5] }}</td>      
                        <td>{{ bid[3] }}</td>
                        <td>{{ bid[4] }}</td>
                        <td>
                            <button @click="cancelBid(bid)">Cancel</button>
                        </td>
                    </tr>
                </table>

                <h2>Sells</h2>
                <table class="Offers">
                    <tr>
                        <th>Date</th>
                        <th>Amount</th>
                        <th>Price</th>
                        <th>Action</th>
                    </tr>
                    <tr v-for="(offer, index) in sellDataList" :key="index">
                        <td>{{ offer[5] }}</td>      
                        <td>{{ offer[3] }}</td>
                        <td>{{ offer[4] }}</td>  
                        <td>
                            <button @click="cancelOffer(offer)">Cancel</button>
                        </td>
                    </tr>
                </table>
            </div>
        </div>
        <div class="stocks">
            <h1>This is the stocks trading page</h1>
            <button @click="fetchStocks">Print bid list</button>
            <button @click="get_database_data_from_server">Fetch Users from DB</button>
            <!-- <button @click="isUserLoggedIn = !isUserLoggedIn">Log in</button> -->
        </div>
        <div>
            <h1 v-if="isUserLoggedIn">Logged in as: {{userName}}</h1>
            <button @click="sendLogoutRequest" v-if="isUserLoggedIn">Log out</button>
            <!-- <div id="login-button"> -->
                <GoogleLogin id="login-button" :callback="sendLoginRequest" v-if="!isUserLoggedIn"/>
            <!-- </div> -->
        </div>
        <!-- <div> -->
        <!--     <input type="sendLoginRequest" v-model="email" /> -->
        <!--     <button @click="sendLoginRequest">Log in</button> -->
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

table {
        width: 100%;
        border-collapse: collapse;
    }
    th, td {
        border: 3px solid #dddddd;
        text-align: left;
        padding: 8px;
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
