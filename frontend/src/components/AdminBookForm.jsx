
import { useState } from "react";
import { addBook } from "../api";

export default function AdminBookForm({ onAdded }) {
  const [form, setForm] = useState({ 
    marker_id: "", 
    title: "", 
    author: "", 
    available: true 
  });
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState({});

  const handle = (e) => {
    const { name, value, type, checked } = e.target;
    setForm({ ...form, [name]: type === "checkbox" ? checked : value });
    
    // Clear error when user starts typing
    if (errors[name]) {
      setErrors({ ...errors, [name]: "" });
    }
  };

  const validateForm = () => {
    const newErrors = {};
    
    if (!form.title.trim()) {
      newErrors.title = "Title is required";
    }
    
    if (!form.author.trim()) {
      newErrors.author = "Author is required";
    }
    
    if (form.marker_id && (isNaN(form.marker_id) || parseInt(form.marker_id) < 0)) {
      newErrors.marker_id = "Marker ID must be a positive number";
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const submit = async (e) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }
    
    setLoading(true);
    try {
      const payload = { 
        ...form, 
        marker_id: form.marker_id ? parseInt(form.marker_id, 10) : null 
      };
      await addBook(payload);
      setForm({ marker_id: "", title: "", author: "", available: true });
      setErrors({});
      onAdded?.();
    } catch (error) {
      console.error("Failed to add book:", error);
      setErrors({ submit: "Failed to add book. Please try again." });
    } finally {
      setLoading(false);
    }
  };

  const resetForm = () => {
    setForm({ marker_id: "", title: "", author: "", available: true });
    setErrors({});
  };

  return (
    <form onSubmit={submit} className="space-y-4">
      {errors.submit && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
          {errors.submit}
        </div>
      )}
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Title *
          </label>
          <input 
            className={`w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 ${
              errors.title ? "border-red-500" : "border-gray-300"
            }`}
            name="title" 
            placeholder="Enter book title" 
            value={form.title} 
            onChange={handle}
            disabled={loading}
          />
          {errors.title && (
            <p className="text-red-600 text-sm mt-1">{errors.title}</p>
          )}
        </div>
        
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Author *
          </label>
          <input 
            className={`w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 ${
              errors.author ? "border-red-500" : "border-gray-300"
            }`}
            name="author" 
            placeholder="Enter author name" 
            value={form.author} 
            onChange={handle}
            disabled={loading}
          />
          {errors.author && (
            <p className="text-red-600 text-sm mt-1">{errors.author}</p>
          )}
        </div>
        
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Marker ID (Optional)
          </label>
          <input 
            className={`w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 ${
              errors.marker_id ? "border-red-500" : "border-gray-300"
            }`}
            name="marker_id" 
            type="number"
            min="0"
            placeholder="Enter marker ID" 
            value={form.marker_id} 
            onChange={handle}
            disabled={loading}
          />
          {errors.marker_id && (
            <p className="text-red-600 text-sm mt-1">{errors.marker_id}</p>
          )}
          <p className="text-gray-500 text-xs mt-1">
            Leave empty if no AR marker is assigned
          </p>
        </div>
        
        <div className="flex items-center">
          <label className="flex items-center space-x-2 cursor-pointer">
            <input 
              type="checkbox" 
              name="available" 
              checked={form.available} 
              onChange={handle}
              disabled={loading}
              className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
            />
            <span className="text-sm font-medium text-gray-700">
              Available for borrowing
            </span>
          </label>
        </div>
      </div>
      
      <div className="flex space-x-3">
        <button 
          type="submit"
          disabled={loading}
          className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading ? "Adding..." : "Add Book"}
        </button>
        <button 
          type="button"
          onClick={resetForm}
          disabled={loading}
          className="px-6 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-gray-500 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          Reset
        </button>
      </div>
    </form>
  );
}
