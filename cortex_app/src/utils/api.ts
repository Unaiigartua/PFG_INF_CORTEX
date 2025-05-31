import config from "../config";

// Get the authentication token from localStorage
const getToken = () => localStorage.getItem("auth_token");

export const api = {
  // Function for authenticated GET requests
  async get(endpoint: string) {
    const token = getToken();
    const headers: HeadersInit = {};
    
    if (token) {
      headers["Authorization"] = `Bearer ${token}`;
    }
    
    const response = await fetch(`${config.API_BASE_URL}${endpoint}`, {
      method: "GET",
      headers
    });
    
    if (!response.ok) {
      throw new Error(`API error: ${response.status}`);
    }
    
    return response.json();
  },
  
  // Function for authenticated POST requests
  async post(endpoint: string, data: any) {
    const token = getToken();
    const headers: HeadersInit = {
      "Content-Type": "application/json"
    };
    
    if (token) {
      headers["Authorization"] = `Bearer ${token}`;
    }
    
    const response = await fetch(`${config.API_BASE_URL}${endpoint}`, {
      method: "POST",
      headers,
      body: JSON.stringify(data)
    });
    
    if (!response.ok) {
      throw new Error(`API error: ${response.status}`);
    }
    
    return response.json();
  }
};