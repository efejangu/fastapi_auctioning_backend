<template>
  <div class="auctions">
    <h1>Active Auctions</h1>
    <div class="auctions-grid">
      <div class="no-auctions" v-if="!auctions.length">
        <p>No active auctions at the moment.</p>
      </div>
      
      <div v-else class="auction-card" v-for="auction in auctions" :key="auction.id">
        <div class="auction-image">
          <img :src="auction.image || 'https://via.placeholder.com/300x200'" :alt="auction.title">
        </div>
        <div class="auction-content">
          <h3>{{ auction.title }}</h3>
          <p class="description">{{ auction.description }}</p>
          <div class="auction-details">
            <span class="current-bid">Current Bid: ${{ auction.currentBid }}</span>
            <span class="time-left">{{ auction.timeLeft }} left</span>
          </div>
          <router-link 
            :to="{ 
              name: 'BidInterface', 
              params: { 
                auctionId: auction.id, 
                title: auction.title 
              } 
            }" 
            class="bid-button"
          >
            Place Bid
          </router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const auctions = ref([])

const fetchAuctions = async () => {
  try {
    const response = await axios.get('http://localhost:8000/auctions')
    auctions.value = response.data.map(auction => ({
      id: auction.id,
      title: auction.title,
      description: auction.description,
      currentBid: auction.current_bid || 0,
      timeLeft: auction.time_left || 'Ending soon',
      image: auction.image_url || null
    }))
  } catch (error) {
    console.error('Error fetching auctions:', error)
  }
}

onMounted(fetchAuctions)
</script>

<style>
@import './css/Auctions.css';

.bid-button {
  display: inline-block;
  background-color: #42b983;
  color: white;
  padding: 10px 15px;
  border-radius: 5px;
  text-decoration: none;
  transition: background-color 0.3s ease;
}

.bid-button:hover {
  background-color: #3aa876;
}
</style>
