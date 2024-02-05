<script lang="ts">
import { getStocks } from '../stocks/Stocks.ts'

export default {
  data() {
    return {
      stocks: []
    }
  },
  methods: {
    async fetchStocks() {
      this.stocks = await getStocks();
    }
  }
}

const callback = (response) => {
  // This callback will be triggered when the user selects or login to
  // his Google account from the popup
  console.log("Handle the response", response)
}

</script>

<template>
  <div class="stocks">
    <h1>This is the stocks trading page</h1>
    <button @click="fetchStocks">Fetch Stocks</button>
  </div>
  <GoogleLogin :callback="callback"/>
</template>

<style>
@media (min-width: 1024px) {
  .stocks {
    display: block;
  }
}
</style>
