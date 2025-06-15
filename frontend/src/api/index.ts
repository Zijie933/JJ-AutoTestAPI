import axios from 'axios';
import { ElMessage } from 'element-plus';
import type { AxiosInstance, AxiosRequestConfig, AxiosResponse, InternalAxiosRequestConfig } from 'axios';
import { BackendResponse } from './types.js'; // Import BackendResponse

// Determine the base URL based on the environment
// const baseURL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:9101';
const baseURL = 'http://127.0.0.1:9101';

const apiClient: AxiosInstance = axios.create({
  baseURL: baseURL,
  timeout: 10000, // 10 seconds timeout
  headers: {
    'Content-Type': 'application/json',
    // You can add other default headers here, like Authorization tokens
  },
});

// Request interceptor for API calls
apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    // Log the request details
    console.log('Request Sent:', {
      url: config.url,
      method: config.method,
      headers: config.headers,
      params: config.params,
      data: config.data,
    });
    // TODO: Add token or other headers if needed
    // const token = localStorage.getItem('token');
    // if (token) {
    //   config.headers.Authorization = `Bearer ${token}`;
    // }
    return config;
  },
  (error) => {
    console.error('Request Error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor for API calls
apiClient.interceptors.response.use(
  (response: AxiosResponse<any>) => { // Use AxiosResponse<any> for flexibility
    // Log the raw response
    console.log('Raw Response Received:', response);

    // Special handling for login route which returns a raw token string
    if (response.config.url === '/user/login' && response.status === 200 && typeof response.data === 'string') {
      console.log('Login Endpoint: Raw token received:', response.data);
      return response.data; // Return the token string directly
    }

    // Existing BackendResponse logic for other routes
    const res = response.data as BackendResponse<any>; // Cast to BackendResponse for other routes

    // Check if res is defined and has a code property (for BackendResponse structure)
    if (res && (res.code === 0 || res.code === 200)) {
      console.log('Successful Response Data:', res.data);
      return res.data; // Return the actual data field from BackendResponse
    } else {
      // Handle backend-specific errors or unexpected structures for non-login routes
      const errorMessage = res?.message || 'Error from backend or unexpected response structure';
      ElMessage.error(errorMessage);
      console.error('Backend Error or Unexpected Structure:', res);
      return Promise.reject(new Error(errorMessage));
    }
  },
  (error) => {
    // Log the full error object for more details
    console.error('Response Error Details:', error);

    if (error.response) {
      // The request was made and the server responded with a status code
      // that falls out of the range of 2xx
      console.error('Error Response Data:', error.response.data);
      console.error('Error Response Status:', error.response.status);
      console.error('Error Response Headers:', error.response.headers);
      ElMessage.error(error.response.data.message || error.message || 'Server Error');
    } else if (error.request) {
      // The request was made but no response was received
      console.error('Error Request:', error.request);
      ElMessage.error('No response from server. Check network or server status.');
    } else {
      // Something happened in setting up the request that triggered an Error
      console.error('Error Message:', error.message);
      ElMessage.error(error.message || 'Request setup error');
    }
    return Promise.reject(error);
  }
);

// Unified request function
// The return type is now Promise<T> where T is the type of 'data' in BackendResponse<T>
const request = <T = any>(config: AxiosRequestConfig): Promise<any> => {
  return apiClient.request<BackendResponse<T>>(config) // Expect BackendResponse<T> from axios
    .then(data => data); // The response interceptor already extracts res.data
};

export { apiClient }; // Export apiClient as a named export
export default request;