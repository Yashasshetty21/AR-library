
import { useState } from "react";
import { deleteBook, updateBook } from "../api";

export default function BookList({ 
  books, 
  refresh, 
  selectedBooks = new Set(), 
  onSelectBook, 
  onSelectAll, 
  showSelection = false 
}) {
  const [editingBook, setEditingBook] = useState(null);
  const [editForm, setEditForm] = useState({});

  const handleEdit = (book) => {
    setEditingBook(book.id);
    setEditForm({
      title: book.title,
      author: book.author,
      marker_id: book.marker_id || "",
      available: book.available
    });
  };

  const handleSave = async (bookId) => {
    try {
      const payload = { ...editForm };
      if (payload.marker_id === "") {
        payload.marker_id = null;
      } else {
        payload.marker_id = parseInt(payload.marker_id);
      }
      await updateBook(bookId, payload);
      setEditingBook(null);
      setEditForm({});
      refresh();
    } catch (error) {
      console.error("Failed to update book:", error);
    }
  };

  const handleCancel = () => {
    setEditingBook(null);
    setEditForm({});
  };

  const handleDelete = async (bookId) => {
    if (!confirm("Are you sure you want to delete this book?")) return;
    try {
      await deleteBook(bookId);
      refresh();
    } catch (error) {
      console.error("Failed to delete book:", error);
    }
  };

  const handleQuickToggle = async (book) => {
    try {
      await updateBook(book.id, { available: !book.available });
      refresh();
    } catch (error) {
      console.error("Failed to toggle book status:", error);
    }
  };

  return (
    <div className="overflow-x-auto">
      <table className="min-w-full">
        <thead className="bg-gray-50 border-b">
          <tr>
            {showSelection && (
              <th className="text-left p-3">
                <input
                  type="checkbox"
                  checked={selectedBooks.size === books.length && books.length > 0}
                  onChange={onSelectAll}
                  className="rounded border-gray-300"
                />
              </th>
            )}
            <th className="text-left p-3 font-medium text-gray-700">ID</th>
            <th className="text-left p-3 font-medium text-gray-700">Title</th>
            <th className="text-left p-3 font-medium text-gray-700">Author</th>
            <th className="text-left p-3 font-medium text-gray-700">Marker ID</th>
            <th className="text-left p-3 font-medium text-gray-700">Status</th>
            <th className="text-left p-3 font-medium text-gray-700">Actions</th>
          </tr>
        </thead>
        <tbody>
          {books.map((book) => (
            <tr key={book.id} className="border-b hover:bg-gray-50">
              {showSelection && (
                <td className="p-3">
                  <input
                    type="checkbox"
                    checked={selectedBooks.has(book.id)}
                    onChange={() => onSelectBook(book.id)}
                    className="rounded border-gray-300"
                  />
                </td>
              )}
              <td className="p-3 text-sm text-gray-600">{book.id}</td>
              <td className="p-3">
                {editingBook === book.id ? (
                  <input
                    type="text"
                    value={editForm.title}
                    onChange={(e) => setEditForm({...editForm, title: e.target.value})}
                    className="w-full px-2 py-1 border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-blue-500"
                  />
                ) : (
                  <span className="font-medium">{book.title}</span>
                )}
              </td>
              <td className="p-3">
                {editingBook === book.id ? (
                  <input
                    type="text"
                    value={editForm.author}
                    onChange={(e) => setEditForm({...editForm, author: e.target.value})}
                    className="w-full px-2 py-1 border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-blue-500"
                  />
                ) : (
                  <span>{book.author}</span>
                )}
              </td>
              <td className="p-3">
                {editingBook === book.id ? (
                  <input
                    type="number"
                    value={editForm.marker_id}
                    onChange={(e) => setEditForm({...editForm, marker_id: e.target.value})}
                    placeholder="Optional"
                    className="w-full px-2 py-1 border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-blue-500"
                  />
                ) : (
                  <span className={book.marker_id ? "text-blue-600 font-medium" : "text-gray-400"}>
                    {book.marker_id || "—"}
                  </span>
                )}
              </td>
              <td className="p-3">
                {editingBook === book.id ? (
                  <select
                    value={editForm.available}
                    onChange={(e) => setEditForm({...editForm, available: e.target.value === "true"})}
                    className="px-2 py-1 border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-blue-500"
                  >
                    <option value={true}>Available</option>
                    <option value={false}>Unavailable</option>
                  </select>
                ) : (
                  <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
                    book.available 
                      ? "bg-green-100 text-green-800" 
                      : "bg-red-100 text-red-800"
                  }`}>
                    {book.available ? "✅ Available" : "❌ Unavailable"}
                  </span>
                )}
              </td>
              <td className="p-3">
                <div className="flex items-center space-x-2">
                  {editingBook === book.id ? (
                    <>
                      <button
                        onClick={() => handleSave(book.id)}
                        className="px-2 py-1 text-xs bg-green-600 text-white rounded hover:bg-green-700"
                      >
                        Save
                      </button>
                      <button
                        onClick={handleCancel}
                        className="px-2 py-1 text-xs bg-gray-600 text-white rounded hover:bg-gray-700"
                      >
                        Cancel
                      </button>
                    </>
                  ) : (
                    <>
                      <button
                        onClick={() => handleEdit(book)}
                        className="px-2 py-1 text-xs bg-blue-600 text-white rounded hover:bg-blue-700"
                      >
                        Edit
                      </button>
                      <button
                        onClick={() => handleQuickToggle(book)}
                        className={`px-2 py-1 text-xs rounded ${
                          book.available 
                            ? "bg-red-600 text-white hover:bg-red-700" 
                            : "bg-green-600 text-white hover:bg-green-700"
                        }`}
                      >
                        {book.available ? "Mark Unavailable" : "Mark Available"}
                      </button>
                      <button
                        onClick={() => handleDelete(book.id)}
                        className="px-2 py-1 text-xs bg-red-800 text-white rounded hover:bg-red-900"
                      >
                        Delete
                      </button>
                    </>
                  )}
                </div>
              </td>
            </tr>
          ))}
          {books.length === 0 && (
            <tr>
              <td className="p-8 text-center text-gray-500" colSpan={showSelection ? 7 : 6}>
                No books found
              </td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  );
}
