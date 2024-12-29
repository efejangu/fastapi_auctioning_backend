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

<style scoped>
.auctions {
  padding: 2rem;
}

h1 {
  margin-bottom: 2rem;
  color: #2c3e50;
}

.auctions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 2rem;
}

.no-auctions {
  grid-column: 1 / -1;
  text-align: center;
  padding: 2rem;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.auction-card {
  background: white;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.auction-image {
  height: 200px;
  overflow: hidden;
}

.auction-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.auction-content {
  padding: 1.5rem;
}

h3 {
  margin: 0 0 0.5rem;
  color: #2c3e50;
}

.description {
  color: #666;
  margin-bottom: 1rem;
}

.auction-details {
  display: flex;
  justify-content: space-between;
  margin-bottom: 1rem;
  font-size: 0.9rem;
}

.current-bid {
  color: #42b983;
  font-weight: bold;
}

.time-left {
  color: #666;
}

.bid-button {
  width: 100%;
  padding: 0.75rem;
  background-color: #42b983;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1rem;
  transition: background-color 0.2s;
}

.bid-button:hover {
  background-color: #3aa876;
}
</style>
