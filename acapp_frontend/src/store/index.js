import Vue from 'vue'
import Vuex from 'vuex'
import events from './modules/events'
import router from './modules/router'
import user from './modules/user'

Vue.use(Vuex)

export default new Vuex.Store({
  modules: {
    events,
    router,
    user
  }
})
