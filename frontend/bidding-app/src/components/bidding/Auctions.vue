<template>
  <div class="auctions">
    <h1>Active Auctions</h1>
    
    <div class="controls">
      <div class="search-bar">
        <input 
          type="text" 
          v-model="searchQuery" 
          placeholder="Search auctions..."
          @input="filterAuctions"
        >
      </div>
      
      <div class="filters">
        <select v-model="priceFilter" @change="filterAuctions">
          <option value="all">All Prices</option>
          <option value="under100">Under $100</option>
          <option value="100to500">$100 - $500</option>
          <option value="over500">Over $500</option>
        </select>
      </div>
    </div>

    <div class="auctions-grid">
      <div class="no-auctions" v-if="!filteredAuctions.length">
        <div v-if="biddingGroups.length">
          <h2>Available Bidding Groups</h2>
          <div class="bidding-groups">
            <div v-for="group in biddingGroups" :key="group.name" class="group-card">
              <h3>{{ group.name }}</h3>
              <p v-if="group.target_price">Target Price: ${{ group.target_price }}</p>
              <router-link 
                :to="{ 
                  name: 'BidInterface',
                  params: { 
                    groupName: group.name 
                  }
                }" 
                class="join-button"
              >
                Join Group
              </router-link>
            </div>
          </div>
        </div>
        <p v-else>No active auctions at the moment.</p>
      </div>
      
      <div v-else class="auction-card" v-for="auction in filteredAuctions" :key="auction.id">
        <div class="auction-image">
          <img :src="auction.image || 'https://via.placeholder.com/300x200'" :alt="auction.title">
        </div>
        <div class="auction-content">
          <h3>{{ auction.title }}</h3>
          <p class="description">{{ auction.description }}</p>
          <div class="auction-details">
            <span class="current-bid">Current Bid: ${{ auction.currentBid }}</span>
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

    <a 
      href="/dashboard"
      class="dashboard-link"
    >
      <font-awesome-icon icon="arrow-left" />
      Back to Dashboard
    </a>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue'
import axios from 'axios'
import webSocketService from '@/services/websocket'

const auctions = ref([])
const biddingGroups = ref([])
const searchQuery = ref('')
const priceFilter = ref('all')

const fetchAuctions = async () => {
  try {
    const response = await axios.get('http://localhost:8000/auctions')
    auctions.value = response.data.map(auction => ({
      id: auction.id,
      title: auction.title,
      description: auction.description,
      currentBid: auction.current_bid || 0,
      image: auction.image_url || null,
      createdAt: auction.created_at
    }))
  } catch (error) {
    console.error('Error fetching auctions:', error)
  }
}

const fetchBiddingGroups = async () => {
  try {
    const response = await axios.get('http://localhost:8000/get_groups', {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      }
    })
    biddingGroups.value = response.data || []
  } catch (error) {
    console.error('Error fetching bidding groups:', error)
    biddingGroups.value = []
  }
}

const handleAuctionUpdate = (updatedAuction) => {
  const index = auctions.value.findIndex(a => a.id === updatedAuction.id)
  if (index !== -1) {
    auctions.value[index] = {
      ...auctions.value[index],
      currentBid: updatedAuction.current_bid
    }
  }
}

const handleNewAuction = (newAuction) => {
  auctions.value.unshift(newAuction)
}

const filteredAuctions = computed(() => {
  let filtered = [...auctions.value]

  // Search filter
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(auction => 
      auction.title.toLowerCase().includes(query) ||
      auction.description.toLowerCase().includes(query)
    )
  }

  // Price filter
  switch (priceFilter.value) {
    case 'under100':
      filtered = filtered.filter(a => a.currentBid < 100)
      break
    case '100to500':
      filtered = filtered.filter(a => a.currentBid >= 100 && a.currentBid <= 500)
      break
    case 'over500':
      filtered = filtered.filter(a => a.currentBid > 500)
      break
  }

  return filtered
})

onMounted(() => {
  fetchAuctions()
  fetchBiddingGroups()
  webSocketService.connectToAuctions()
  webSocketService.onAuctionUpdate(handleAuctionUpdate)
  webSocketService.onNewAuction(handleNewAuction)
})

onUnmounted(() => {
  webSocketService.disconnect()
})
</script>

<style scoped>
@import url('./css/Auctions.css');
</style>
