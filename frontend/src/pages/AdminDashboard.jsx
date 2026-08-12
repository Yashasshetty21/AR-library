
import { useEffect, useState } from "react";
import { getAllBooks, updateBook, deleteBook } from "../api";
import AdminBookForm from "../components/AdminBookForm";
import BookList from "../components/BookList";

export default function AdminDashboard() {
  const [books, setBooks] = useState([]);
  const [filteredBooks, setFilteredBooks] = useState([]);
  const [searchTerm, setSearchTerm] = useState("");
  const [statusFilter, setStatusFilter] = useState("all");
  const [selectedBooks, setSelectedBooks] = useState(new Set());
  const [showAddForm, setShowAddForm] = useState(false);
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState({
    total: 0,
    available: 0,
    unavailable: 0,
    withMarkers: 0,
    withoutMarkers: 0
  });

  const refresh = async () => {
    setLoading(true);
    try {
      const allBooks = await getAllBooks();
      setBooks(allBooks);
      updateStats(allBooks);
    } catch (error) {
      console.error("Failed to fetch books:", error);
    } finally {
      setLoading(false);
    }
  };

  const updateStats = (bookList) => {
    const total = bookList.length;
    const available = bookList.filter(b => b.available).length;
    const unavailable = total - available;
    const withMarkers = bookList.filter(b => b.marker_id !== null && b.marker_id !== undefined).length;
    const withoutMarkers = total - withMarkers;
    
    setStats({ total, available, unavailable, withMarkers, withoutMarkers });
  };

  useEffect(() => { 
    refresh(); 
  }, []);

  // Filter books based on search and status
  useEffect(() => {
    let filtered = books;
    
    if (searchTerm) {
      filtered = filtered.filter(book => 
        book.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
        book.author.toLowerCase().includes(searchTerm.toLowerCase()) ||
        book.id.toString().includes(searchTerm) ||
        (book.marker_id && book.marker_id.toString().includes(searchTerm))
      );
    }
    
    if (statusFilter !== "all") {
      filtered = filtered.filter(book => {
        if (statusFilter === "available") return book.available;
        if (statusFilter === "unavailable") return !book.available;
        if (statusFilter === "withMarkers") return book.marker_id !== null && book.marker_id !== undefined;
        if (statusFilter === "withoutMarkers") return book.marker_id === null || book.marker_id === undefined;
        return true;
      });
    }
    
    setFilteredBooks(filtered);
  }, [books, searchTerm, statusFilter]);

  // Bulk operations
  const handleBulkStatusChange = async (newStatus) => {
    if (selectedBooks.size === 0) return;
    
    const promises = Array.from(selectedBooks).map(id => 
      updateBook(id, { available: newStatus })
    );
    
    try {
      await Promise.all(promises);
      setSelectedBooks(new Set());
      refresh();
    } catch (error) {
      console.error("Failed to update books:", error);
    }
  };

  const handleBulkDelete = async () => {
    if (selectedBooks.size === 0) return;
    
    if (!confirm(`Are you sure you want to delete ${selectedBooks.size} book(s)?`)) return;
    
    const promises = Array.from(selectedBooks).map(id => deleteBook(id));
    
    try {
      await Promise.all(promises);
      setSelectedBooks(new Set());
      refresh();
    } catch (error) {
      console.error("Failed to delete books:", error);
    }
  };

  const handleSelectAll = () => {
    if (selectedBooks.size === filteredBooks.length) {
      setSelectedBooks(new Set());
    } else {
      setSelectedBooks(new Set(filteredBooks.map(b => b.id)));
    }
  };

  const handleSelectBook = (bookId) => {
    const newSelected = new Set(selectedBooks);
    if (newSelected.has(bookId)) {
      newSelected.delete(bookId);
    } else {
      newSelected.add(bookId);
    }
    setSelectedBooks(newSelected);
  };

  const exportBooks = () => {
    const csvContent = [
      ["ID", "Title", "Author", "Available", "Marker ID"],
      ...filteredBooks.map(book => [
        book.id,
        book.title,
        book.author,
        book.available ? "Yes" : "No",
        book.marker_id || ""
      ])
    ].map(row => row.join(",")).join("\n");
    
    const blob = new Blob([csvContent], { type: "text/csv" });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "books_export.csv";
    a.click();
    window.URL.revokeObjectURL(url);
  };

  return (
    <div className="space-y-6 p-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-gray-800">Admin Dashboard</h1>
        <div className="space-x-2">
          <button
            onClick={() => setShowAddForm(!showAddForm)}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            {showAddForm ? "Hide Add Form" : "Add New Book"}
          </button>
          <button
            onClick={exportBooks}
            className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
          >
            Export CSV
          </button>
        </div>
      </div>

      {/* Statistics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
        <div className="bg-white p-4 rounded-lg shadow border">
          <div className="text-2xl font-bold text-blue-600">{stats.total}</div>
          <div className="text-sm text-gray-600">Total Books</div>
        </div>
        <div className="bg-white p-4 rounded-lg shadow border">
          <div className="text-2xl font-bold text-green-600">{stats.available}</div>
          <div className="text-sm text-gray-600">Available</div>
        </div>
        <div className="bg-white p-4 rounded-lg shadow border">
          <div className="text-2xl font-bold text-red-600">{stats.unavailable}</div>
          <div className="text-sm text-gray-600">Unavailable</div>
        </div>
        <div className="bg-white p-4 rounded-lg shadow border">
          <div className="text-2xl font-bold text-purple-600">{stats.withMarkers}</div>
          <div className="text-sm text-gray-600">With Markers</div>
        </div>
        <div className="bg-white p-4 rounded-lg shadow border">
          <div className="text-2xl font-bold text-orange-600">{stats.withoutMarkers}</div>
          <div className="text-sm text-gray-600">Without Markers</div>
        </div>
      </div>

      {/* Add Book Form */}
      {showAddForm && (
        <div className="bg-white p-6 rounded-lg shadow border">
          <h2 className="text-xl font-semibold mb-4">Add New Book</h2>
          <AdminBookForm onAdded={() => { refresh(); setShowAddForm(false); }} />
        </div>
      )}

      {/* Search and Filters */}
      <div className="bg-white p-4 rounded-lg shadow border">
        <div className="flex flex-col md:flex-row gap-4">
          <div className="flex-1">
            <input
              type="text"
              placeholder="Search by title, author, ID, or marker ID..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div className="flex gap-2">
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="all">All Books</option>
              <option value="available">Available Only</option>
              <option value="unavailable">Unavailable Only</option>
              <option value="withMarkers">With Markers</option>
              <option value="withoutMarkers">Without Markers</option>
            </select>
          </div>
        </div>
      </div>

      {/* Bulk Operations */}
      {selectedBooks.size > 0 && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <div className="flex items-center justify-between">
            <span className="text-yellow-800">
              {selectedBooks.size} book(s) selected
            </span>
            <div className="space-x-2">
              <button
                onClick={() => handleBulkStatusChange(true)}
                className="px-3 py-1 bg-green-600 text-white rounded hover:bg-green-700"
              >
                Mark Available
              </button>
              <button
                onClick={() => handleBulkStatusChange(false)}
                className="px-3 py-1 bg-red-600 text-white rounded hover:bg-red-700"
              >
                Mark Unavailable
              </button>
              <button
                onClick={handleBulkDelete}
                className="px-3 py-1 bg-red-800 text-white rounded hover:bg-red-900"
              >
                Delete Selected
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Books Table */}
      <div className="bg-white rounded-lg shadow border">
        {loading ? (
          <div className="p-8 text-center">
            <div className="text-gray-500">Loading books...</div>
          </div>
        ) : (
          <BookList 
            books={filteredBooks} 
            refresh={refresh}
            selectedBooks={selectedBooks}
            onSelectBook={handleSelectBook}
            onSelectAll={handleSelectAll}
            showSelection={true}
          />
        )}
      </div>

      {/* Results Summary */}
      <div className="text-sm text-gray-600 text-center">
        Showing {filteredBooks.length} of {books.length} books
        {searchTerm && ` matching "${searchTerm}"`}
        {statusFilter !== "all" && ` (${statusFilter} filter applied)`}
      </div>
    </div>
  );
}
