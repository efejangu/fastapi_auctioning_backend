<template>
  <div class="bid-interface">
    <!-- Add error/success messages -->
    <div v-if="message" :class="['message', messageType]">
      {{ message }}
    </div>

    <div class="bid-status">
      <h2>Current Bid Status</h2>
      <div class="status-details">
        <p class="current-bid">Current Bid: ${{ currentBid }}</p>
        <p class="time-remaining" v-if="timeRemaining">Time Remaining: {{ timeRemaining }}</p>
        <p class="status-message" :class="bidStatus.toLowerCase()">{{ bidStatus }}</p>
      </div>
    </div>

    <div class="bid-controls">
      <div class="preset-buttons">
        <button 
          v-for="amount in presetAmounts" 
          :key="amount"
          @click="placeBid(amount)"
          class="bid-button"
          :disabled="!isConnected"
        >
          ${{ amount }}
        </button>
      </div>

      <div class="custom-bid">
        <div class="input-group">
          <span class="currency-symbol">$</span>
          <input
            type="number"
            v-model="customAmount"
            placeholder="Enter custom amount"
            min="0"
            step="0.01"
            class="custom-amount-input"
            :disabled="!isConnected"
          />
        </div>
        <button 
          @click="placeBid(customAmount)"
          class="submit-bid-button"
          :disabled="!isValidCustomAmount || !isConnected"
        >
          Place Custom Bid
        </button>
      </div>
    </div>
  </div>

  <router-link 
    to="/dashboard" 
    class="dashboard-link"
    @click="navigateToDashboard"
  >
    <font-awesome-icon icon="arrow-left" />
    Back to Dashboard
  </router-link>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'

const route = useRoute()
const router = useRouter()
const currentBid = ref(0)
const customAmount = ref('')
const timeRemaining = ref('')
const bidStatus = ref('OPEN')
const presetAmounts = [50, 150, 300, 500]
const message = ref('')
const messageType = ref('')
const isConnected = ref(false)

const showMessage = (text, type = 'success') => {
  message.value = text
  messageType.value = type
  setTimeout(() => {
    message.value = ''
    messageType.value = ''
  }, 3000)
}

const isValidCustomAmount = computed(() => {
  const amount = Number(customAmount.value)
  return amount > currentBid.value && !isNaN(amount)
})

const placeBid = async (amount) => {
  try {
    if (!ws || ws.readyState !== WebSocket.OPEN) {
      showMessage('Not connected to bidding server. Please try again.', 'error')
      return
    }

    const bidAmount = Number(amount)
    if (bidAmount <= currentBid.value) {
      showMessage('Bid must be higher than current bid', 'error')
      return
    }

    ws.send(JSON.stringify({
      type: 'place_bid',
      amount: bidAmount,
      group_name: route.params.groupName
    }))
    
    customAmount.value = ''
    showMessage('Bid placed successfully')
  } catch (error) {
    console.error('Error placing bid:', error)
    showMessage('Failed to place bid. Please try again.', 'error')
  }
}

let ws
let reconnectAttempts = 0
const MAX_RECONNECT_ATTEMPTS = 5

const connectWebSocket = () => {
  try {
    ws = new WebSocket(`ws://localhost:8000/bidding/ws/connect?group_name=${route.params.groupName}`)
    
    ws.onopen = () => {
      isConnected.value = true
      reconnectAttempts = 0
      showMessage('Connected to bidding server')
    }

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        if (data.type === 'bid_update') {
          currentBid.value = data.amount
          bidStatus.value = data.status
          timeRemaining.value = data.timeRemaining
          
          if (data.message) {
            showMessage(data.message, data.status === 'error' ? 'error' : 'success')
          }
        }
      } catch (error) {
        console.error('Error processing message:', error)
      }
    }

    ws.onclose = () => {
      isConnected.value = false
      if (reconnectAttempts < MAX_RECONNECT_ATTEMPTS) {
        reconnectAttempts++
        showMessage(`Disconnected from bidding server. Reconnecting (${reconnectAttempts}/${MAX_RECONNECT_ATTEMPTS})...`, 'error')
        setTimeout(connectWebSocket, 3000)
      } else {
        showMessage('Unable to connect to bidding server after multiple attempts', 'error')
      }
    }

    ws.onerror = () => {
      showMessage('Connection error. Please try again later.', 'error')
    }
  } catch (error) {
    console.error('WebSocket connection error:', error)
    showMessage('Failed to connect to bidding server', 'error')
  }
}

const navigateToDashboard = async () => {
  await router.push('/dashboard')
  window.location.reload()
}

onMounted(() => {
  connectWebSocket()
})

onUnmounted(() => {
  if (ws) {
    ws.close()
  }
})
</script>

<style scoped>
.bid-interface {
  max-width: 800px;
  margin: 2rem auto;
  padding: 2rem;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.message {
  padding: 1rem;
  margin-bottom: 1rem;
  border-radius: 8px;
  text-align: center;
  font-weight: 500;
}

.message.success {
  background-color: #42b98333;
  color: #42b983;
  border: 1px solid #42b983;
}

.message.error {
  background-color: #e74c3c33;
  color: #e74c3c;
  border: 1px solid #e74c3c;
}

.bid-status {
  text-align: center;
  margin-bottom: 2rem;
  padding-bottom: 1.5rem;
  border-bottom: 1px solid #eee;
}

.status-details {
  display: flex;
  justify-content: space-around;
  margin-top: 1rem;
}

.current-bid {
  font-size: 1.5rem;
  font-weight: bold;
  color: #2c3e50;
}

.status-message {
  font-weight: bold;
}

.status-message.open {
  color: #42b983;
}

.status-message.closed {
  color: #e74c3c;
}

.bid-controls {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.preset-buttons {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 1rem;
}

.bid-button {
  padding: 1rem;
  font-size: 1.2rem;
  background-color: #42b983;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.bid-button:hover:not(:disabled) {
  background-color: #3aa876;
  transform: translateY(-1px);
}

.bid-button:disabled {
  background-color: #ccc;
  cursor: not-allowed;
  transform: none;
}

.custom-bid {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.input-group {
  position: relative;
  display: flex;
  align-items: center;
}

.currency-symbol {
  position: absolute;
  left: 1rem;
  color: #666;
}

.custom-amount-input {
  width: 100%;
  padding: 1rem;
  padding-left: 2rem;
  font-size: 1.2rem;
  border: 2px solid #ddd;
  border-radius: 8px;
  outline: none;
  transition: all 0.2s;
}

.custom-amount-input:focus:not(:disabled) {
  border-color: #42b983;
}

.custom-amount-input:disabled {
  background-color: #f5f5f5;
  cursor: not-allowed;
}

.submit-bid-button {
  padding: 1rem;
  font-size: 1.2rem;
  background-color: #2c3e50;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.submit-bid-button:hover:not(:disabled) {
  background-color: #34495e;
  transform: translateY(-1px);
}

.submit-bid-button:disabled {
  background-color: #ccc;
  cursor: not-allowed;
  transform: none;
}

.time-remaining {
  color: #666;
}

.dashboard-link {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  margin-top: 2rem;
  padding: 0.5rem 1rem;
  color: #2c3e50;
  text-decoration: none;
  font-weight: 500;
  transition: color 0.2s;
}

.dashboard-link:hover {
  color: #42b983;
}
</style>