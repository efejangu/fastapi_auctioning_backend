<template>
  <div class="create-bid-container">
    <!-- Sidebar Navigation -->
    <div class="create-bid-sidebar">
      <div class="sidebar-logo">
        <font-awesome-icon icon="gavel" class="logo-icon" />
        <h2>BidFlow</h2>
      </div>
      
      <ul class="sidebar-menu">
        <li 
          v-for="(menu, index) in sidebarMenus" 
          :key="index"
          :class="['sidebar-menu-item', { active: activeSection === menu.id }]"
          @click="activeSection = menu.id"
        >
          <font-awesome-icon :icon="menu.icon" class="icon" />
          <span>{{ menu.label }}</span>
        </li>
      </ul>
    </div>

    <!-- Main Content Area -->
    <div class="create-bid-main">
      <!-- Bid Creation Form -->
      <section v-if="activeSection === 'create'" class="bid-form-section">
        <div class="bid-form-header">
          <h2>Create New Bid Group</h2>
        </div>

        <form @submit.prevent="createBidGroup">
          <div class="form-group">
            <label>Group Name</label>
            <div class="input-wrapper">
              <input 
                type="text" 
                v-model="bidGroup.name" 
                class="form-control" 
                placeholder="Enter group name"
                required
              />
              <font-awesome-icon icon="tag" class="input-icon" />
            </div>
          </div>

          <div class="form-group">
            <label>Target Price</label>
            <div class="input-wrapper">
              <input 
                type="number" 
                v-model.number="bidGroup.targetPrice" 
                class="form-control" 
                placeholder="Set target price"
                min="0"
                step="0.01"
                required
              />
              <font-awesome-icon icon="dollar-sign" class="input-icon" />
            </div>
          </div>

          <button type="submit" class="create-bid-btn">
            Create Bid Group
          </button>
        </form>
      </section>

      <!-- Bid Groups Monitoring -->
      <section v-if="activeSection === 'monitor'" class="bid-groups-section">
        <div class="bid-groups-header">
          <h2>Bid Groups</h2>
          <button @click="activeSection = 'create'" class="create-bid-btn">
            Create New
          </button>
        </div>

        <div class="bid-groups-list">
          <div 
            v-for="group in bidGroups" 
            :key="group.id" 
            class="bid-group-card"
          >
            <div class="bid-group-card-header">
              <div class="bid-group-card-title">{{ group.name }}</div>
              <div class="bid-group-card-status">
                {{ group.status }}
              </div>
            </div>

            <div class="bid-group-card-details">
              <div>
                <div class="label">Target Price</div>
                <span>${{ group.targetPrice.toFixed(2) }}</span>
              </div>
              <div>
                <div class="label">Current Bid</div>
                <span>${{ group.currentBid.toFixed(2) }}</span>
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { library } from '@fortawesome/fontawesome-svg-core'
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome'
import { 
  faTag, 
  faDollarSign, 
  faClock, 
  faPlusCircle, 
  faChartBar,
  faGavel 
} from '@fortawesome/free-solid-svg-icons'

library.add(
  faTag, 
  faDollarSign, 
  faClock, 
  faPlusCircle, 
  faChartBar,
  faGavel
)

const activeSection = ref('create')
const socket = ref(null)

const sidebarMenus = [
  { id: 'create', label: 'Create Bid', icon: 'plus-circle' },
  { id: 'monitor', label: 'Monitor Bids', icon: 'chart-bar' }
]

const bidGroup = ref({
  name: '',
  targetPrice: null
})

const bidGroups = ref([])

const connectWebSocket = () => {
  socket.value = new WebSocket('ws://localhost:8000/bidding/ws/connect')
  
  socket.value.onopen = () => {
    console.log('WebSocket connected')
  }
  
  socket.value.onmessage = (event) => {
    const data = JSON.parse(event.data)
    console.log('Received:', data)
    // Handle incoming messages
  }
  
  socket.value.onerror = (error) => {
    console.error('WebSocket error:', error)
  }
}

const createBidGroup = async () => {
  try {
    const createGroupSocket = new WebSocket(`ws://localhost:8000/bidding/ws/create_group?group_name=${bidGroup.value.name}&target_price=${bidGroup.value.targetPrice}`)
    
    createGroupSocket.onopen = () => {
      console.log('Create group connection opened')
    }
    
    createGroupSocket.onmessage = (event) => {
      const response = JSON.parse(event.data)
      console.log('Group created:', response)
      
      // Reset form and switch to monitoring
      bidGroup.value = {
        name: '',
        targetPrice: null
      }
      activeSection.value = 'monitor'
      
      // Close this specific connection
      createGroupSocket.close()
    }
  } catch (error) {
    console.error('Error creating bid group:', error)
  }
}

onMounted(() => {
  connectWebSocket()
})
</script>

<style scoped>
/* Import external styles first */
@import url('./css/CreateBid.css');
</style>