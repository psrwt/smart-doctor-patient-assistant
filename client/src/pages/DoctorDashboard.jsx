import React, { useEffect, useState } from "react";
import axios from "axios";
import { useAuth } from "../context/AuthContext";
import ChatBox from "../components/ChatBox";

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL;

export default function DoctorDashboard() {
  const { user, logout } = useAuth();
  const token = localStorage.getItem("token");

  useEffect(() => {
    const fetchData = async () => {
      try {
        const res = await axios.get(`${BACKEND_URL}/doctor/dashboard`, {
          headers: { Authorization: `Bearer ${token}` },
        });
      } catch (err) {
        console.error(err);
      }
    };
    fetchData();
  }, [token]);

  const handleLogout = () => {
    logout();
    window.location.href = "/auth";
  };

  return (
    <div className="h-screen flex bg-gradient-to-br from-emerald-50 to-cyan-100">
      {/* ✅ SIDEBAR */}
      <aside className="w-72 bg-white/80 backdrop-blur-xl shadow-xl border-r border-white/40 flex flex-col p-6">
        <div>
          <h2 className="text-2xl font-bold text-emerald-600 mb-8">
            🧑‍⚕️ Doctor Panel
          </h2>

          {/* Avatar */}
          <div className="flex items-center gap-3 mb-6">
            <div className="w-12 h-12 rounded-full bg-emerald-600 text-white flex items-center justify-center text-lg font-bold">
              {user?.user_name?.[0]?.toUpperCase()}
            </div>
            <div>
              <p className="font-semibold">{user?.user_name}</p>
              <p className="text-xs text-gray-500">{user?.user_email}</p>
            </div>
          </div>

          <div className="space-y-3 text-sm text-gray-700">
            <div className="flex justify-between">
              <span className="font-medium">Role</span>
              <span className="capitalize">{user?.user_role}</span>
            </div>
          </div>
        </div>

        <button
          onClick={handleLogout}
          className="mt-auto bg-red-500/90 hover:bg-red-600 hover:cursor-pointer text-white py-2 rounded-xl transition shadow-md"
        >
          Logout
        </button>
      </aside>

      {/* ✅ MAIN AREA */}
      <main className="flex-1 flex flex-col">
        {/* Header */}
        <header className="bg-white/80 backdrop-blur border-b border-white/40 shadow-sm px-6 py-4 flex justify-between items-center">
          <h1 className="text-lg font-semibold">AI Medical Assistant 💬</h1>
          <span className="text-sm text-gray-500">Doctor Workspace</span>
        </header>

        {/* CHAT AREA */}
        <ChatBox />
      </main>
    </div>
  );
}
