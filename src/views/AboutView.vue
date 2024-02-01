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
  <button @click="fetchStocks">Fetch Stocks</button>
  <div class="about">
    <h1>This is an about page</h1>

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
