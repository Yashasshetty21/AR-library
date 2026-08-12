
import { Link, useLocation, useNavigate } from "react-router-dom";

export default function Navbar() {
  const { pathname } = useLocation();
  const navigate = useNavigate();
  const isAdmin = localStorage.getItem("isAdmin") === "true";

  const link = (to, label) => (
    <Link
      to={to}
      className={`px-3 py-2 rounded ${pathname === to ? 'bg-white text-purple-600' : 'hover:bg-purple-500/30'}`}
    >
      {label}
    </Link>
  );

  const handleLogout = () => {
    localStorage.removeItem("isAdmin");
    navigate("/admin/login");
  };

  return (
    <nav className="bg-purple-600 text-white">
      <div className="max-w-5xl mx-auto flex items-center justify-between p-4">
        <div className="font-bold text-lg">📚 AR Library</div>
        <div className="space-x-2">
          {link("/", "Scanner")}
          {isAdmin ? (
            <button
              onClick={handleLogout}
              className="px-3 py-2 rounded hover:bg-purple-500/30 text-sm"
            >
              Logout
            </button>
          ) : (
            link("/admin", "Admin")
          )}
        </div>
      </div>
    </nav>
  );
}
