<template>
  <div class="dashboard-container">
    <div class="dashboard-header">
      <h1>Dashboard</h1>
      <div class="user-info">
        <img 
          :src="userProfile.avatar || 'https://via.placeholder.com/50'" 
          alt="User Avatar" 
          class="user-avatar"
        />
        <div class="user-details">
          <span class="user-name">{{ userProfile.name }}</span>
          <span class="user-role">{{ userProfile.role }}</span>
        </div>
        <button @click="handleLogout" class="logout-button">Logout</button>
      </div>
    </div>

    <div class="dashboard-stats">
      <div class="stats-grid">
        <router-link to="/auctions" class="stat-card">
          <div class="stat-icon">
            <font-awesome-icon icon="store" />
          </div>
          <div class="stat-content">
            <h3>Active Auctions</h3>
            <div class="stat-value">{{ activeAuctionsCount }}</div>
            <div class="stat-trend positive">
              <font-awesome-icon icon="arrow-up" />
              {{ auctionsTrend }}% this week
            </div>
          </div>
        </router-link>

        <router-link to="/create-bid" class="stat-card">
          <div class="stat-icon">
            <font-awesome-icon icon="plus-circle" />
          </div>
          <div class="stat-content">
            <h3>Create Auction</h3>
            <div class="stat-value">Start Bidding</div>
            <div class="stat-trend">New Opportunity</div>
          </div>
        </router-link>

        <div class="stat-card">
          <div class="stat-icon">
            <font-awesome-icon icon="bookmark" />
          </div>
          <div class="stat-content">
            <h3>My Bids</h3>
            <div class="stat-value">{{ myBidsCount }}</div>
            <div class="stat-trend">Total Bids</div>
          </div>
        </div>
      </div>
    </div>

    <div class="dashboard-recent-activity">
      <h2>Recent Activity</h2>
      <div class="activity-list">
        <div 
          v-for="activity in recentActivities" 
          :key="activity.id" 
          class="activity-item"
        >
          <div class="activity-icon">
            <font-awesome-icon :icon="activity.icon" />
          </div>
          <div class="activity-details">
            <span class="activity-title">{{ activity.title }}</span>
            <span class="activity-time">{{ activity.time }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { useRouter } from 'vue-router'
import { authService } from '@/services/auth'

const router = useRouter()
const activeAuctionsCount = ref(0)
const myBidsCount = ref(0)
const auctionsTrend = ref(12)

const userProfile = ref({
  name: 'John Doe',
  role: 'Bidder',
  avatar: null
})

const recentActivities = ref([
  {
    id: 1,
    title: 'Bid placed on Vintage Watch',
    time: '2 mins ago',
    icon: 'gavel'
  },
  {
    id: 2,
    title: 'New auction created',
    time: '1 hour ago',
    icon: 'store'
  },
  {
    id: 3,
    title: 'Outbid on Rare Coin Collection',
    time: '3 hours ago',
    icon: 'arrow-up'
  }
])

const handleLogout = () => {
  authService.logout()
}

</script>

<style scoped>
@import './css/Dashboard.css';

.logout-button {
  margin-left: 1rem;
  padding: 0.5rem 1rem;
  background-color: #4cffd6;
  color: #ffffff;
  border: none;
  border-radius: 5px;
  cursor: pointer;
}

.logout-button:hover {
  background-color: #3bbfbf;
}
</style>
