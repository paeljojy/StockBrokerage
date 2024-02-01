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
</script>

<template>
  <div class="stocks">
    <h1>This is an stocks trading page</h1>
    <button @click="fetchStocks">Fetch Stocks</button>
  </div>
</template>

<style>
@media (min-width: 1024px) {
  .about {
    min-height: 100vh;
    display: flex;
    align-items: center;
  }
}
</style>
