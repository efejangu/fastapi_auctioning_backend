import { io } from 'socket.io-client'
import { WebSocket } from 'websocket'

class WebSocketService {
  constructor() {
    this.socket = null
    this.wsSocket = null
    this.baseURL = 'ws://localhost:8000'
    this.auctionCallbacks = {
      onUpdate: null,
      onNew: null
    }
  }

  // Socket.IO connection method
  connectSocketIO(path) {
    const fullURL = `${this.baseURL}${path}`
    this.socket = io(fullURL, {
      transports: ['websocket'],
      reconnection: true,
      reconnectionAttempts: 5,
      reconnectionDelay: 1000
    })

    this.socket.on('connect', () => {
      console.log('Socket.IO WebSocket connected')
    })

    this.socket.on('disconnect', () => {
      console.log('Socket.IO WebSocket disconnected')
    })

    this.socket.on('connect_error', (error) => {
      console.error('Socket.IO WebSocket connection error:', error)
    })

    return this.socket
  }

  // Native WebSocket connection method
  connectWebSocket(path) {
    const fullURL = `${this.baseURL}${path}`
    this.wsSocket = new WebSocket(fullURL)

    this.wsSocket.onopen = () => {
      console.log('Native WebSocket connected')
    }

    this.wsSocket.onclose = () => {
      console.log('Native WebSocket disconnected')
    }

    this.wsSocket.onerror = (error) => {
      console.error('Native WebSocket connection error:', error)
    }

    return this.wsSocket
  }

  // Methods for Socket.IO
  createBidGroup(groupName, targetPrice) {
    if (!this.socket) {
      throw new Error('Socket.IO WebSocket not connected')
    }
    this.socket.emit('create_group', { group_name: groupName, target_price: targetPrice })
  }

  placeBidSocketIO(groupName, bid) {
    if (!this.socket) {
      throw new Error('Socket.IO WebSocket not connected')
    }
    this.socket.emit('place_bid', { group_name: groupName, bid })
  }

  onBidUpdateSocketIO(callback) {
    if (!this.socket) {
      throw new Error('Socket.IO WebSocket not connected')
    }
    this.socket.on('bid_update', callback)
  }

  // Methods for Native WebSocket
  sendWebSocketMessage(message) {
    if (!this.wsSocket || this.wsSocket.readyState !== WebSocket.OPEN) {
      throw new Error('Native WebSocket not connected')
    }
    this.wsSocket.send(JSON.stringify(message))
  }

  onWebSocketMessage(callback) {
    if (!this.wsSocket) {
      throw new Error('Native WebSocket not connected')
    }
    this.wsSocket.onmessage = (event) => {
      callback(JSON.parse(event.data))
    }
  }

  // Auction specific methods
  connectToAuctions() {
    const wsSocket = this.connectWebSocket('/ws/auctions')
    
    wsSocket.onmessage = (event) => {
      const data = JSON.parse(event.data)
      if (data.type === 'auction_update' && this.auctionCallbacks.onUpdate) {
        this.auctionCallbacks.onUpdate(data.auction)
      } else if (data.type === 'new_auction' && this.auctionCallbacks.onNew) {
        this.auctionCallbacks.onNew(data.auction)
      }
    }

    wsSocket.onclose = () => {
      console.log('Auction WebSocket disconnected')
      // Attempt to reconnect after a delay
      setTimeout(() => this.connectToAuctions(), 3000)
    }

    return wsSocket
  }

  onAuctionUpdate(callback) {
    this.auctionCallbacks.onUpdate = callback
  }

  onNewAuction(callback) {
    this.auctionCallbacks.onNew = callback
  }

  disconnect() {
    if (this.socket) {
      this.socket.disconnect()
      this.socket = null
    }

    if (this.wsSocket) {
      this.wsSocket.close()
      this.wsSocket = null
    }
  }
}

export const webSocketService = new WebSocketService()
export default webSocketService
