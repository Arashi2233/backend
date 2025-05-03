import axios from 'axios'
//别人的

const UserManagement = {
  urls: {
    register: 'http://127.0.0.1:8000/register/',
    signup: 'http://127.0.0.1:8000/login/',
  },
  async register(user) {
    return (await axios.post(this.urls.register, user)).data.success
  },
  async signup(user) {
    const response = await axios.post(this.urls.signup, user)
    return response.data
  },
}

export default UserManagement
