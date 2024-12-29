import { createApp } from 'vue'
import App from './App.vue'
import router from './router'

/* import the fontawesome core */
import { library } from '@fortawesome/fontawesome-svg-core'

/* import font awesome icon component */
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome'

/* import specific icons */
import { 
    faHouse,
    faStore,
    faBookmark,
    faUser,
    faArrowRightFromBracket
} from '@fortawesome/free-solid-svg-icons'

/* add icons to the library */
library.add(
    faHouse,
    faStore,
    faBookmark,
    faUser,
    faArrowRightFromBracket
)

const app = createApp(App)

app.component('font-awesome-icon', FontAwesomeIcon)
app.use(router)

app.mount('#app')
