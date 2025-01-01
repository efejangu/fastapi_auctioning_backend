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

const activeAuctionsCount = ref(0)
const myBidsCount = ref(0)
const auctionsTrend = ref(12)  // Example trend percentage

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

const fetchDashboardStats = async () => {
  try {
    const [auctionsResponse, bidsResponse, userResponse] = await Promise.all([
      axios.get('http://localhost:8000/auctions/count'),
      axios.get('http://localhost:8000/bids/my-bids/count'),
      axios.get('http://localhost:8000/user/profile')
    ])

    activeAuctionsCount.value = auctionsResponse.data.count
    myBidsCount.value = bidsResponse.data.count
    userProfile.value = userResponse.data
  } catch (error) {
    console.error('Error fetching dashboard stats:', error)
  }
}

onMounted(fetchDashboardStats)
</script>

<style scoped>
.dashboard-container {
  background-color: #1a1a2e;
  color: #ffffff;
  min-height: 100vh;
  padding: 2rem;
}

.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

h1 {
  font-size: 2rem;
  color: #4cffd6;
  margin: 0;
}

.user-info {
  display: flex;
  align-items: center;
  background-color: #16213e;
  padding: 0.75rem 1.5rem;
  border-radius: 50px;
}

.user-avatar {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  margin-right: 1rem;
  border: 3px solid #4cffd6;
}

.user-details {
  display: flex;
  flex-direction: column;
}

.user-name {
  font-weight: bold;
  color: #4cffd6;
}

.user-role {
  font-size: 0.8rem;
  color: #8892b0;
}

.dashboard-stats {
  margin-bottom: 2rem;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1.5rem;
}

.stat-card {
  background-color: #16213e;
  border-radius: 15px;
  padding: 1.5rem;
  display: flex;
  align-items: center;
  transition: transform 0.3s ease;
  text-decoration: none;
  color: inherit;
}

.stat-card:hover {
  transform: scale(1.05);
  background-color: #0f3460;
}

.stat-icon {
  font-size: 2.5rem;
  color: #4cffd6;
  margin-right: 1.5rem;
}

.stat-content {
  flex-grow: 1;
}

.stat-content h3 {
  margin: 0 0 0.5rem 0;
  color: #8892b0;
  font-size: 1rem;
}

.stat-value {
  font-size: 1.75rem;
  font-weight: bold;
  color: #4cffd6;
  margin-bottom: 0.5rem;
}

.stat-trend {
  font-size: 0.8rem;
  color: #8892b0;
}

.stat-trend.positive {
  color: #4cffd6;
}

.dashboard-recent-activity {
  background-color: #16213e;
  border-radius: 15px;
  padding: 1.5rem;
}

.dashboard-recent-activity h2 {
  margin: 0 0 1rem 0;
  color: #4cffd6;
  font-size: 1.25rem;
}

.activity-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.activity-item {
  display: flex;
  align-items: center;
  background-color: #0f3460;
  padding: 1rem;
  border-radius: 10px;
}

.activity-icon {
  font-size: 1.5rem;
  color: #4cffd6;
  margin-right: 1rem;
}

.activity-details {
  display: flex;
  flex-direction: column;
}

.activity-title {
  font-weight: bold;
  color: #ffffff;
}

.activity-time {
  font-size: 0.8rem;
  color: #8892b0;
}
</style>
