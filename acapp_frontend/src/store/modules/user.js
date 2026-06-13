const state = {
    accessToken: null,
    refreshToken: null,
    user: null
}

const mutations = {
    setTokens(state, { accessToken, refreshToken }) {
        state.accessToken = accessToken
        state.refreshToken = refreshToken
    },
    setUser(state, user) {
        state.user = user
    },
    logout(state) {
        state.accessToken = null
        state.refreshToken = null
        state.user = null
    }
}

const actions = {
    login({ commit }, { accessToken, refreshToken, user }) {
        commit('setTokens', { accessToken, refreshToken })
        commit('setUser', user)
    },
    logout({ commit }) {
        commit('logout')
    }
}

export default {
    state,
    mutations,
    actions
}
