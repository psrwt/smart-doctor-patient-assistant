import { useState } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL;

export default function SignupForm() {
    const navigate = useNavigate();
    const [name, setName] = useState("");
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [role, setRole] = useState("patient");
    const [loading, setLoading] = useState(false);

    const {login} = useAuth();

    const handleSubmit = async (e) => {
        e.preventDefault();

        try {
            setLoading(true);

            const res = await axios.post(`${BACKEND_URL}/auth/signup`, {
                full_name: name,
                email,
                password,
                role,
            });

            const { access_token, user_role, user_name, user_email, user_id } = res.data;

            login({ user_name, user_email, user_id, user_role }, access_token);

            alert("Account created successfully");

            if (user_role === "doctor") navigate("/doctor"); else navigate("/patient");

        } catch (err) {
            console.error(err);
            alert(err.response?.data?.detail || "Signup failed");
        } finally {
            setLoading(false);
        }
    };

    return (
        <form onSubmit={handleSubmit} className="space-y-4">
            <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                    Name
                </label>
                <input
                    required
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    className="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="Enter your name"
                />
            </div>

            <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                    Email
                </label>
                <input
                    type="email"
                    required
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="you@example.com"
                />
            </div>

            <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                    Password
                </label>
                <input
                    type="password"
                    required
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="Create strong password"
                />
            </div>

            {/* Role Selector */}
            <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                    Register as
                </label>

                <div className="grid grid-cols-2 gap-3">
                    <button
                        type="button"
                        onClick={() => setRole("patient")}
                        className={`py-2 rounded-lg border font-medium transition
              ${role === "patient"
                                ? "bg-blue-600 text-white border-blue-600"
                                : "bg-gray-100 hover:bg-gray-200"
                            }`}
                    >
                        Patient
                    </button>

                    <button
                        type="button"
                        onClick={() => setRole("doctor")}
                        className={`py-2 rounded-lg border font-medium transition
              ${role === "doctor"
                                ? "bg-blue-600 text-white border-blue-600"
                                : "bg-gray-100 hover:bg-gray-200"
                            }`}
                    >
                        Doctor
                    </button>
                </div>
            </div>

            <button
                disabled={loading}
                className="w-full bg-indigo-600 hover:bg-indigo-700 text-white py-2 rounded-lg font-semibold transition disabled:opacity-60"
            >
                {loading ? "Creating..." : "Create Account"}
            </button>
        </form>
    );
}
