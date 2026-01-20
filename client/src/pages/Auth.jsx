import { useState } from "react";
import LoginForm from "../components/LoginForm";
import SignupForm from "../components/SignupForm";

export default function Auth() {
    const [mode, setMode] = useState("login");

    return (
        <div className="min-h-screen flex items-center justify-center bg-linear-to-br from-blue-50 to-indigo-100 px-4">
            <div className="w-full max-w-md bg-white rounded-2xl shadow-xl p-8">
                <h2 className="text-2xl font-bold text-center mb-6 text-gray-800">
                    {mode === "login" ? "Welcome 👋" : "Create Account 🚀"}
                </h2>

                {mode === "login" ? <LoginForm /> : <SignupForm />}

                <p className="text-sm text-center mt-6 text-gray-600">
                    {mode === "login" ? (
                        <>
                            Don’t have an account?{" "}
                            <button
                                onClick={() => setMode("signup")}
                                className="text-blue-600 font-semibold hover:underline"
                            >
                                Create account
                            </button>
                        </>
                    ) : (
                        <>
                            Already have an account?{" "}
                            <button
                                onClick={() => setMode("login")}
                                className="text-blue-600 font-semibold hover:underline"
                            >
                                Login
                            </button>
                        </>
                    )}
                </p>
            </div>
        </div>
    );
}
