
import { Routes, Route, Navigate, useLocation } from "react-router-dom";
import Navbar from "./components/Navbar";
import PublicScanner from "./pages/PublicScanner";
import AdminDashboard from "./pages/AdminDashboard";
import AdminLogin from "./components/AdminLogin";

function SimpleAdminRoute({ children }) {
  const isAdmin = localStorage.getItem("isAdmin") === "true";
  const location = useLocation();
  if (!isAdmin) {
    return <Navigate to="/admin/login" state={{ from: location }} replace />;
  }
  return children;
}

export default function App() {
  return (
    <div>
      <Navbar />
      <div className="max-w-5xl mx-auto p-4">
        <Routes>
          <Route path="/" element={<PublicScanner />} />
          <Route path="/admin/login" element={<AdminLogin />} />
          <Route
            path="/admin"
            element={
              <SimpleAdminRoute>
                <AdminDashboard />
              </SimpleAdminRoute>
            }
          />
        </Routes>
      </div>
    </div>
  );
}
