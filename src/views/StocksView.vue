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
    <h1>This is the stocks trading page</h1>
    <button @click="fetchStocks">Fetch Stocks</button>
  </div>
</template>

<style>
@media (min-width: 1024px) {
  .stocks {
    display: block;
  }
}
</style>
