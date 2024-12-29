<template>
  <div class="dashboard">
    <h1>Dashboard</h1>
    <div class="stats-grid">
      <div class="stat-card">
        <font-awesome-icon icon="store" class="icon" />
        <div class="stat-content">
          <h3>Active Auctions</h3>
          <p class="stat-value">0</p>
        </div>
      </div>
      
      <div class="stat-card">
        <font-awesome-icon icon="bookmark" class="icon" />
        <div class="stat-content">
          <h3>My Bids</h3>
          <p class="stat-value">0</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
// Dashboard logic will go here
</script>

<style scoped>
.dashboard {
  padding: 2rem;
}

h1 {
  margin-bottom: 2rem;
  color: #2c3e50;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
}

.stat-card {
  background: white;
  padding: 1.5rem;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
}

.icon {
  font-size: 2rem;
  color: #42b983;
  margin-right: 1rem;
}

.stat-content {
  flex: 1;
}

h3 {
  margin: 0;
  color: #666;
  font-size: 1rem;
}

.stat-value {
  margin: 0.5rem 0 0;
  font-size: 1.5rem;
  font-weight: bold;
  color: #2c3e50;
}
</style>
