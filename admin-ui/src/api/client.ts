import axios from 'axios'

const api = axios.create({
  baseURL: '/api/admin',
})

export default api
