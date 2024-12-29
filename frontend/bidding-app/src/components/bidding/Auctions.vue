<template>
  <div class="auctions">
    <h1>Active Auctions</h1>
    <div class="auctions-grid">
      <div class="no-auctions" v-if="!auctions.length">
        <p>No active auctions at the moment.</p>
      </div>
      
      <div v-else class="auction-card" v-for="auction in auctions" :key="auction.id">
        <div class="auction-image">
          <img :src="auction.image" :alt="auction.title">
        </div>
        <div class="auction-content">
          <h3>{{ auction.title }}</h3>
          <p class="description">{{ auction.description }}</p>
          <div class="auction-details">
            <span class="current-bid">Current Bid: ${{ auction.currentBid }}</span>
            <span class="time-left">{{ auction.timeLeft }} left</span>
          </div>
          <button class="bid-button">Place Bid</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const auctions = ref([
  // Sample data - replace with actual API calls
  {
    id: 1,
    title: 'Sample Auction',
    description: 'This is a sample auction item.',
    currentBid: 100,
    timeLeft: '2 days',
    image: 'https://via.placeholder.com/300x200'
  }
])
</script>

<style>
@import './css/Auctions.css';
</style>
