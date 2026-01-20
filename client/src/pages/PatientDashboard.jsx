import React, { useEffect, useState } from "react";
import axios from "axios";

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL;

export default function PatientDashboard() {
  const [message, setMessage] = useState("");
  const token = localStorage.getItem("token");

  useEffect(() => {
    const fetchData = async () => {
      try {
        const res = await axios.get(`${BACKEND_URL}/patient/dashboard`, {
          headers: { Authorization: `Bearer ${token}` },
        });
        setMessage(res.data.msg);
      } catch (err) {
        console.error(err);
        setMessage("Error: Unauthorized or server error");
      }
    };
    fetchData();
  }, [token]);

  const handleLogout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("role");
    window.location.href = "/auth";
  };

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gray-100">
      <div className="bg-white p-8 rounded shadow-md w-96 text-center">
        <h1 className="text-2xl font-bold mb-4">Patient Dashboard</h1>
        <p className="mb-4">{message}</p>
        <button
          onClick={handleLogout}
          className="px-4 py-2 bg-red-500 text-white rounded hover:bg-red-600"
        >
          Logout
        </button>
      </div>
    </div>
  );
}
