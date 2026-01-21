import { useState } from "react";
import axios from "axios";

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL;

export default function ChatBox() {
  const [messages, setMessages] = useState([
    { role: "assistant", text: "Hello! How can I help you today? 😊" },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  const token = localStorage.getItem("token");

  const sendMessage = async () => {
    if (!input.trim()) return;

    const userMsg = { role: "user", text: input };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");

    try {
      setLoading(true);

      const res = await axios.post(
        `${BACKEND_URL}/agent/chat`,
        { message: input, messages: messages },
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      const botMsg = {
        role: "assistant",
        text: res.data.reply || "No response from agent",
      };

      setMessages((prev) => [...prev, botMsg]);
    } catch (err) {
      console.error(err);
      setMessages((prev) => [
        ...prev,
        { role: "assistant", text: "⚠️ Server error. Try again later." },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex-1 flex flex-col p-6 overflow-hidden">
      {/* MESSAGES */}
      <div className="flex-1 overflow-y-auto space-y-4 pr-2">
        {messages.map((m, i) => (
          <div
            key={i}
            className={`max-w-xl px-4 py-3 rounded-2xl shadow-sm text-sm leading-relaxed ${
              m.role === "user"
                ? "bg-indigo-600 text-white ml-auto rounded-br-sm"
                : "bg-white/80 backdrop-blur text-gray-900 rounded-bl-sm"
            }`}
          >
            {m.text}
          </div>
        ))}

        {loading && (
          <div className="text-sm text-gray-500 italic">
            typing...
          </div>
        )}
      </div>

      {/* INPUT BAR */}
      <div className="mt-4 flex items-center gap-3 bg-white/80 backdrop-blur p-3 rounded-2xl shadow-lg">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && sendMessage()}
          placeholder="Describe your symptoms..."
          className="flex-1 bg-transparent outline-none px-2 text-sm"
        />

        <button
          onClick={sendMessage}
          disabled={loading}
          className="bg-indigo-600 hover:bg-indigo-700 text-white px-5 py-2 rounded-xl transition disabled:opacity-50"
        >
          Send
        </button>
      </div>
    </div>
  );
}
