
import axios from "axios";

export const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

export const api = axios.create({
  baseURL: API_URL,
});

// Add auth token to requests
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('admin_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Handle auth errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('admin_token');
      localStorage.removeItem('admin_user');
      window.location.href = '/admin/login';
    }
    return Promise.reject(error);
  }
);

// Returns an array of books; supports both `{ books: [...] }` and `[...]` shapes
export const getAllBooks = () =>
  api.get("/admin/books").then(r => (Array.isArray(r.data) ? r.data : (r.data && r.data.books) || []));
export const getBooksByMarker = (markerId) => api.get(`/books/marker/${markerId}`).then(r => r.data);
export const addBook = (payload) => api.post("/admin/books", payload).then(r => r.data);
export const updateBook = (id, payload) => api.put(`/admin/books/${id}`, payload).then(r => r.data);
export const deleteBook = (id) => api.delete(`/admin/books/${id}`).then(r => r.data);

// Additional functions for enhanced admin features
export const bulkUpdateBooks = (bookIds, payload) => 
  api.put("/admin/books/bulk", { book_ids: bookIds, ...payload }).then(r => r.data);

export const bulkDeleteBooks = (bookIds) => 
  api.delete("/admin/books/bulk", { data: { book_ids: bookIds } }).then(r => r.data);

export const getBookStats = () => api.get("/admin/books/stats").then(r => r.data);

export const searchBooks = (query) => 
  api.get("/admin/books/search", { params: { q: query } }).then(r => r.data);

// Authentication functions
export const loginAdmin = (credentials) => 
  api.post("/admin/auth/login", credentials).then(r => r.data);

export const logoutAdmin = () => 
  api.post("/admin/auth/logout").then(r => r.data);

export const verifyToken = () => 
  api.get("/admin/auth/verify").then(r => r.data);
