const API_BASE_URL = 'https://ecommerce-chatbot-e5zr.onrender.com/api';

export const apiCall = async (endpoint, method = 'GET', data = null, token = null) => {
  const url = `${API_BASE_URL}${endpoint}`;
  
  const config = {
    method,
    headers: {
      'Content-Type': 'application/json',
    },
  };

  if (token) {
    config.headers['Authorization'] = `Bearer ${token}`;
  } else {
    const storedToken = localStorage.getItem('token');
    if (storedToken) {
      config.headers['Authorization'] = `Bearer ${storedToken}`;
    }
  }

  if (data) {
    config.body = JSON.stringify(data);
  }

  try {
    const response = await fetch(url, config);
    const responseData = await response.json();

    if (!response.ok) {
      throw new Error(responseData.message || 'API request failed');
    }

    return responseData;
  } catch (error) {
    throw error;
  }
};

export const chatAPI = {
  sendMessage: (message) => apiCall('/chat', 'POST', { message }),
  getChatHistory: () => apiCall('/chat-history', 'GET'),
};

export const productsAPI = {
  getAllProducts: () => apiCall('/products', 'GET'),
  searchProducts: (params) => {
    const queryString = new URLSearchParams(params).toString();
    return apiCall(`/products/search?${queryString}`, 'GET');
  },
  getProductsByCategory: (category) => apiCall(`/products/category/${category}`, 'GET'),
};