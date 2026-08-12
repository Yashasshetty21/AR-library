# 🚀 AR Library System

A comprehensive Augmented Reality library management system that combines your proven Python AR detection with a modern web interface.

## ✨ Features

### 🎯 **AR Marker Detection**
- **Python-based OpenCV ArUco detection** - Your proven AR system
- **Real-time camera processing** - Instant marker recognition
- **Multiple marker support** - Handle multiple books per marker
- **Beautiful UI overlays** - Professional AR experience

### 📚 **Library Management**
- **Comprehensive Admin Dashboard** - Full book management
- **Search & Filter** - Find books quickly
- **Bulk Operations** - Manage multiple books at once
- **Statistics Dashboard** - Library insights
- **Export Functionality** - CSV export for analysis

### 🔧 **Technical Features**
- **FastAPI Backend** - High-performance Python API
- **React Frontend** - Modern, responsive UI
- **PostgreSQL Database** - Reliable data storage
- **Real-time Updates** - Live data synchronization

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.8+
- Node.js 16+
- PostgreSQL
- Camera (for AR functionality)

### Quick Start

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd ar-library-project
   ```

2. **Run the startup script**
   ```bash
   python start_ar_library.py
   ```

   This script will:
   - ✅ Check prerequisites
   - ✅ Set up the database
   - ✅ Install dependencies
   - ✅ Start both servers
   - ✅ Open the application

### Manual Setup

If you prefer manual setup:

1. **Set up the database**
   ```bash
   cd backend
   python setup_ar_database.py
   ```

2. **Install Python dependencies**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

3. **Install frontend dependencies**
   ```bash
   cd frontend
   npm install
   ```

4. **Start the backend**
   ```bash
   cd backend
   uvicorn app:app --host 0.0.0.0 --port 8000 --reload
   ```

5. **Start the frontend**
   ```bash
   cd frontend
   npm run dev
   ```

## 🎮 Usage

### 📱 **Public Scanner**
- Visit: `http://localhost:5173/scanner`
- Point your camera at ArUco markers
- View available books instantly
- Auto-scanning every 2 seconds

### 📊 **Admin Dashboard**
- Visit: `http://localhost:5173/admin`
- Add, edit, and manage books
- Search and filter functionality
- Bulk operations
- Export data

### 🔍 **API Endpoints**
- **Health Check**: `GET /health`
- **Detect Marker**: `POST /detect-marker`
- **Get Books by Marker**: `GET /markers/{marker_id}/books`
- **Available Markers**: `GET /markers/available`
- **Camera Status**: `GET /camera-status`

## 📋 **Database Schema**

### Shelves Table
```sql
CREATE TABLE shelves (
    id SERIAL PRIMARY KEY,
    marker_id INTEGER UNIQUE NOT NULL,
    shelf_name VARCHAR(200) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Books Table
```sql
CREATE TABLE books (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    author VARCHAR(100) NOT NULL,
    marker_id INTEGER REFERENCES shelves(marker_id),
    available BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 🎯 **ArUco Markers**

The system uses **4x4 ArUco markers** (DICT_4X4_50). 

### Sample Marker IDs
- **Marker 1**: Science Fiction
- **Marker 2**: Computer Science
- **Marker 3**: Literature
- **Marker 4**: History

### Creating Markers
You can generate ArUco markers using:
- OpenCV's `cv2.aruco.drawMarker()`
- Online ArUco generators
- Print markers and place them on bookshelves

## 🔧 **Configuration**

### Database Configuration
Edit `backend/setup_ar_database.py`:
```python
DB_CONFIG = {
    'dbname': 'ar_library',
    'user': 'postgres',
    'password': 'Post',
    'host': 'localhost',
    'port': '5432'
}
```

### API Configuration
Edit `frontend/src/api.js`:
```javascript
export const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";
```

## 🚀 **Advanced Features**

### Custom AR Processing
Your Python AR scripts are integrated as:
- `backend/ar_library_postgres.py` - Main AR detection
- `backend/setup_postgres.py` - AR setup and utilities

### Extending the System
1. **Add new AR features** - Modify the Python scripts
2. **Custom UI components** - Add React components
3. **Additional API endpoints** - Extend FastAPI
4. **Database modifications** - Update schema as needed

## 🐛 **Troubleshooting**

### Camera Issues
- **Permission denied**: Allow camera access in browser
- **Camera in use**: Close other camera applications
- **No camera found**: Check device connections

### Database Issues
- **Connection failed**: Verify PostgreSQL is running
- **Authentication error**: Check database credentials
- **Table not found**: Run `setup_ar_database.py`

### Frontend Issues
- **Dependencies**: Run `npm install` in frontend directory
- **Build errors**: Check Node.js version compatibility
- **API errors**: Verify backend is running on port 8000

## 📝 **Development**

### Project Structure
```
ar-library-project/
├── backend/
│   ├── app.py                 # FastAPI application
│   ├── ar_library_postgres.py # Your AR detection script
│   ├── setup_postgres.py      # AR utilities
│   ├── setup_ar_database.py   # Database setup
│   └── requirements.txt       # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── components/        # React components
│   │   ├── pages/            # Page components
│   │   └── api.js            # API utilities
│   └── package.json          # Node.js dependencies
└── start_ar_library.py       # Startup script
```

### Contributing
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 **License**

This project is licensed under the MIT License.

## 🤝 **Support**

For support and questions:
- Check the troubleshooting section
- Review the API documentation
- Test with sample markers first

---

**🎉 Enjoy your integrated AR Library System!**
