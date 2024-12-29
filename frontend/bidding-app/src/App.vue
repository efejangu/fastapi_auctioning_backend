<template>
  <div id="app">
    <router-view></router-view>
  </div>
</template>

<script setup>
// Component setup logic will go here
</script>

<style>
:root {
  --primary-color: #42b983;
  --primary-dark: #3aa876;
  --bg-dark: #1a1a1a;
  --bg-darker: #121212;
  --text-light: #ffffff;
  --text-gray: #cccccc;
  --border-color: #333;
  --card-bg: #242424;
}

* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

body {
  background-color: var(--bg-dark);
  color: var(--text-light);
  font-family: Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

#app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

input {
  background-color: var(--bg-darker);
  color: var(--text-light);
  border: 1px solid var(--border-color);
}

input::placeholder {
  color: var(--text-gray);
  opacity: 0.7;
}

input:focus {
  outline: none;
  border-color: var(--primary-color);
}

button {
  background-color: var(--primary-color);
  color: white;
  border: none;
  cursor: pointer;
  transition: background-color 0.2s;
  font-weight: 500;
}

button:hover {
  background-color: var(--primary-dark);
}

a {
  color: var(--primary-color);
  text-decoration: none;
  font-weight: 500;
}

a:hover {
  text-decoration: underline;
}

label {
  color: var(--text-light);
  font-weight: 500;
}
</style>
