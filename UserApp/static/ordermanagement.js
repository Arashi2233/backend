import axios from 'axios'
 //别人的

let OrderManagement = {
  urls: {
    main: 'http://127.0.0.1:8000/',
    all_orders: 'http://127.0.0.1:8000/department',
    order: 'http://127.0.0.1:8000/orders/', // 这个是请求顺序的url
  },
  async get_all_orders() {
    let response = await axios.get(this.urls.all_orders)
    return response.data
  },
  async delete_id(id) {
    try {
      await axios.delete(this.urls.all_orders + '/' + id)
    } catch (error) {
      alert(error)
    }
  },
  async add_order(order) {
    try {
      await axios.post(this.urls.all_orders, order)
    } catch (error) {
      alert(error)
    }
  },
  async change_order(id, order) {
    try {
      await axios.put(`${this.urls.all_orders}/${id}`, order)
    } catch (error) {
      console.log(error)
    }
  },
  async default_order() {
    try {
      let response = await axios.get(this.urls.order)
      return response.data
    } catch (error) {
      alert(error)
    }
  },
}

export default OrderManagement
