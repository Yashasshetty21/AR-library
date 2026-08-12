
import { useState, useCallback } from "react";
import MarkerScanner from "../components/MarkerScanner";

export default function PublicScanner() {
  const [markerData, setMarkerData] = useState(null);
  const [loading, setLoading] = useState(false);

  const onDetected = useCallback(async (markerId, markerInfo) => {
    setMarkerData(markerInfo);
    setLoading(false);
  }, []);

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-semibold">Public Scanner</h1>
      
      {/* Marker Information */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <h2 className="text-lg font-semibold text-blue-800 mb-2">📱 Available Markers</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
          <div className="bg-white p-3 rounded border">
            <div className="font-semibold text-blue-600">Marker 0</div>
            <div className="text-gray-600">Science Fiction</div>
            <div className="text-xs text-gray-500">Dune, The Martian, Foundation</div>
          </div>
          <div className="bg-white p-3 rounded border">
            <div className="font-semibold text-blue-600">Marker 1</div>
            <div className="text-gray-600">Computer Science</div>
            <div className="text-xs text-gray-500">Python, Data Structures, ML</div>
          </div>
          <div className="bg-white p-3 rounded border">
            <div className="font-semibold text-blue-600">Marker 2</div>
            <div className="text-gray-600">Literature</div>
            <div className="text-xs text-gray-500">Pride & Prejudice, 1984, Gatsby</div>
          </div>
        </div>
        <p className="text-xs text-blue-600 mt-2">
          💡 Use the marker images from your AR_Library_Project_Complete/markers/ folder
        </p>
      </div>
      
      <MarkerScanner onDetected={onDetected} />

      <div className="mt-4">
        {markerData && (
          <div className="bg-white rounded-lg shadow border p-6">
            <div className="mb-4">
              <h2 className="text-xl font-bold text-blue-600 mb-2">
                📚 {markerData.shelf_name}
              </h2>
              <p className="text-sm text-gray-600">
                Marker ID: <span className="font-mono bg-gray-100 px-2 py-1 rounded">{markerData.marker_id}</span>
              </p>
            </div>
            
            {loading && (
              <div className="text-center py-4">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
                <p className="text-gray-600 mt-2">Loading books...</p>
              </div>
            )}
            
            {!loading && markerData.books && markerData.books.length > 0 && (
              <div className="space-y-3">
                <h3 className="text-lg font-semibold text-gray-800">Available Books:</h3>
                {markerData.books.map((book, index) => (
                  <div key={index} className="p-4 rounded-lg border bg-gray-50 hover:bg-gray-100 transition-colors">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="font-medium text-gray-900">{book.title}</div>
                        <div className="text-sm text-gray-600">by {book.author}</div>
                      </div>
                      <div className="ml-4">
                        {book.available ? (
                          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                            ✅ Available
                          </span>
                        ) : (
                          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">
                            ❌ Unavailable
                          </span>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
            
            {!loading && markerData && (!markerData.books || markerData.books.length === 0) && (
              <div className="text-center py-8">
                <div className="text-gray-400 text-6xl mb-4">📖</div>
                <p className="text-gray-600">
                  {markerData.shelf_name === 'Unknown marker' ? 'Marker not configured in database.' : 'No books found for this shelf.'}
                </p>
                <p className="text-sm text-gray-500 mt-1">This shelf might be empty or the marker is not configured.</p>
              </div>
            )}
          </div>
        )}
        
        {!markerData && !loading && (
          <div className="text-center py-8 text-gray-500">
            <div className="text-4xl mb-4">📱</div>
            <p>Point your camera at an ArUco marker to see available books</p>
            <p className="text-sm mt-2">Using your proven AR detection system</p>
          </div>
        )}
      </div>
    </div>
  );
}
