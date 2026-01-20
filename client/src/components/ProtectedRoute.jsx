import { Navigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function ProtectedRoute({ children, allowedRoles }) {
  const { user } = useAuth();

  if (!user) return <Navigate to="/auth" />;

  if (!allowedRoles.includes(user.user_role)) return <Navigate to="/auth" />;

  return children;
}
