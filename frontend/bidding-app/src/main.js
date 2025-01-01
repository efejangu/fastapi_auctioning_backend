import { createApp } from 'vue'
import App from './App.vue'
import router from './router'

/* Import FontAwesome core */
import { library } from '@fortawesome/fontawesome-svg-core'
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome'
import { 
    faTag, 
    faDollarSign, 
    faChartLine, 
    faClock, 
    faPlusCircle, 
    faChartBar,
    faStore 
} from '@fortawesome/free-solid-svg-icons'

/* Add icons to the library */
library.add(
    faTag, 
    faDollarSign, 
    faChartLine, 
    faClock, 
    faPlusCircle, 
    faChartBar,
    faStore
)

const app = createApp(App)

/* Register FontAwesome component globally */
app.component('font-awesome-icon', FontAwesomeIcon)

app.use(router)
app.mount('#app')
