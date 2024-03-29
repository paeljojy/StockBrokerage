<script lang="ts">
import { getLastTradedPriceForStock } from '../stocks/StocksAPI'
import { getDB } from '../stocks/StocksAPI'
import { getTrades } from '../stocks/StocksAPI'
import { getBidsFromServer } from '../stocks/StocksAPI'
import { getStockAndMoneyFromServer } from '../stocks/StocksAPI'
import { sendLogin } from '../stocks/StocksAPI'
import { sendLogout } from '../stocks/StocksAPI'
import { sendBidCancellationRequest } from '../stocks/StocksAPI'
import { sendOfferCancellationRequest } from '../stocks/StocksAPI'
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
            isAdminLoggedIn: false,
            isUserLoggedIn: false,
            // TODO: could wrap user data in an object
            userFirstName: '',
            userLastName: '',
            loginCredential: {},
            amount: 0,
            price: 0,
            stockCount: 0,
            moneyCount: 0,
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
            tradeDataList: [] as {
                buyer: string;
                seller: string;
                stock_id: number;
                amount: number;
                price: number;
                date: string;
            }[],
            // TODO: Query these from the server when we open the stock page
            currentStock: {
                id: 1,
                name: 'Apple, Inc (AAPL)',
                price: undefined,
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
        async requestTrades() {
            try {
                this.tradeDataList = await getTrades();
                console.log("Server Trades:");
                console.log(this.tradeDataList);
            } catch (error) {
                console.error("Error fetching bids:", error);
            }
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
            this.fetchStockAndMoney();
        },
        formatPrice() {
            this.price = parseFloat(this.price.toFixed(2)); // Rounds to nearest (up to) 2 decimals
        },
        formateDate(dateTimeString) {
            const date = new Date(dateTimeString);
            const options = { year: 'numeric', month: 'numeric', day: 'numeric', hour: '2-digit', minute: '2-digit' };
            return new Intl.DateTimeFormat('default', options).format(date);
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
        async fetchStockAndMoney() {
            const data = await getStockAndMoneyFromServer(this.loginCredential, this.currentStock.id);

            // INFO: At the moment we only have one stock, so we can just take the first element
            // later when we have multiple stocks, we will have to iterate through the array
            this.stockCount = data[0][0];
            this.moneyCount = data[1][0];
        },
        async cancelBid(bid) {
            const bidData = {
                id: bid[0],
                stock_id: bid[2]
            };
            const response = await sendBidCancellationRequest(this.loginCredential, bidData);
            this.requestBids();
            this.fetchStockAndMoney();
        },
        async cancelOffer(offer) {
            const offerData = {
                id: offer[0],
                stock_id: offer[2]
            };
            const response = await sendOfferCancellationRequest(this.loginCredential, offerData);
            this.requestBids();
            this.fetchStockAndMoney();
        },
        async requestBidAddition() {
            // INFO: We are not setting the bid id here, 
            // because the server will determine that as the bid is actually being added
            const newBidData = {
                user_id: this.loginCredential.sub,
                stock_id: this.currentStock.id,
                amount: this.amount,
                price: this.price
            };

            console.log("Ord(number) - amount: " + this.amount + " price: @ " + this.price);

            const response = await sendBidAdditionRequest(this.loginCredential, newBidData);
            this.requestBids();
            this.fetchStockAndMoney();
        },
        async requestSellAddition() {
            const newSellData = {
                user_id: this.loginCredential.sub,
                stock_id: this.currentStock.id,
                amount: this.amount,
                price: this.price
            };

            console.log("Ord(number) - amount: " + this.amount + " price: @ " + this.price);
            const response = await sendSellAdditionRequest(this.loginCredential, newSellData);
            this.requestBids();
            this.fetchStockAndMoney();
        }
    },
    mounted() {
        // FIXME: Ask server if the user is logged in
        // this doesn't work atm as the promise returned by this function is not awaited?
        sendLogin(this.loginCredential).then(temp => console.log("")).then(value => this.isUserLoggedIn = value);
        if (this.isUserLoggedIn)
        {
            this.fetchStockAndMoney();
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
                <div v-if="isUserLoggedIn" class="price"> {{currentStock.price}} USD</div>
                <div v-else class="price">Please log in to see the price</div>
            </header>
            <div class="stock-count" v-if="isUserLoggedIn">Money on this server: {{ moneyCount }} USD</div>
            <div class="stock-count" v-if="isUserLoggedIn">Stocks owned: {{ stockCount }}</div>
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
                        <td>{{ formateDate(bid[5]) }}</td>      
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
                        <td>{{ formateDate(offer[5]) }}</td>      
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
            <!-- <h1>This is the stocks trading page</h1> -->
            <button v-if="isUserLoggedIn" @click="fetchStocks">Print bid list</button>
            <button v-if="isUserLoggedIn" @click="get_database_data_from_server">Fetch Users from DB</button>
            <!-- <button @click="isUserLoggedIn = !isUserLoggedIn">Log in</button> -->
        </div>
        <div class="login-button-container">
            <h1 v-if="isUserLoggedIn">Logged in as: {{userName}}</h1>
            <button @click="sendLogoutRequest" v-if="isUserLoggedIn">Log out</button>
            <GoogleLogin id="login-button" :callback="sendLoginRequest" v-if="!isUserLoggedIn"/>
        </div>
        <div v-if="isUserLoggedIn">
            <h2>Trades made on this server</h2>
            <table class="Bids">
                <tr>
                    <th>Stock</th>
                    <th>Amount</th>
                    <th>Price</th>
                    <th>Date</th>
                    <th v-if="isAdminLoggedIn">Buyer</th>
                    <th v-if="isAdminLoggedIn">Seller</th>
                </tr>
                <tr v-for="(trade, index) in tradeDataList" :key="index">      
                    <td>Apple, Inc (AAPL)</td>
                    <td>{{ trade[3] }}</td>
                    <td>{{ trade[4] }}</td>
                    <td>{{ formateDate(trade[5]) }}</td>
                    <td v-if="isAdminLoggedIn">{{ trade[0] }}</td>
                    <td v-if="isAdminLoggedIn">{{ trade[1] }}</td>
                </tr>
            </table>
            <button @click="requestTrades">Fetch server trades</button>
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

.login-button-container {
  display: flex;
  justify-content: center;
  align-items: center;
}

</style>
