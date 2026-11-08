import { Link, useLocation } from "react-router-dom";
import { motion } from "framer-motion";
import { useTheme } from "../hooks/useTheme";

export default function Navbar() {
  const { theme, toggle } = useTheme();
  const { pathname } = useLocation();

  const links = [
    { to: "/", label: "Analyze" },
    { to: "/history", label: "History" },
  ];

  return (
    <motion.nav
      initial={{ y: -20, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.5 }}
      className="fixed top-0 left-0 right-0 z-50 flex items-center justify-between px-6 py-4"
      style={{
        background: "rgba(9,9,15,0.8)",
        backdropFilter: "blur(20px)",
        borderBottom: "1px solid rgba(255,255,255,0.06)",
      }}
    >
      {/* Logo */}
      <Link to="/" className="flex items-center gap-2.5 group">
        <div className="w-8 h-8 rounded-lg flex items-center justify-center text-lg"
          style={{ background: "linear-gradient(135deg,#6272f5,#8b5cf6)" }}>
          🧠
        </div>
        <span className="font-display font-bold text-lg gradient-text">
          SentimentAI
        </span>
      </Link>

      {/* Nav Links */}
      <div className="flex items-center gap-1">
        {links.map(({ to, label }) => (
          <Link
            key={to}
            to={to}
            className="relative px-4 py-1.5 rounded-full text-sm font-medium transition-colors"
            style={{
              color: pathname === to ? "#fff" : "var(--text-secondary)",
            }}
          >
            {pathname === to && (
              <motion.span
                layoutId="nav-pill"
                className="absolute inset-0 rounded-full"
                style={{ background: "rgba(98,114,245,0.2)", border: "1px solid rgba(98,114,245,0.4)" }}
                transition={{ type: "spring", stiffness: 300, damping: 30 }}
              />
            )}
            <span className="relative">{label}</span>
          </Link>
        ))}
      </div>

      {/* Theme Toggle */}
      <button
        onClick={toggle}
        className="w-9 h-9 rounded-full flex items-center justify-center text-lg transition-all hover:scale-110"
        style={{ background: "rgba(255,255,255,0.06)", border: "1px solid rgba(255,255,255,0.1)" }}
        aria-label="Toggle theme"
      >
        {theme === "dark" ? "☀️" : "🌙"}
      </button>
    </motion.nav>
  );
}
