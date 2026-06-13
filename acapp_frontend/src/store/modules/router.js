const state = {
    router_name: 'calendar',
    router_params: {}
}

const mutations = {
    updateRouterName(state, name) {
        state.router_name = name
    },
    updateRouterParams(state, params) {
        state.router_params = params
    }
}

const actions = {
    changeView({ commit }, { name, params = {} }) {
        commit('updateRouterName', name)
        commit('updateRouterParams', params)
    }
}

export default {
    state,
    mutations,
    actions
}
