import './App.css'
import { Routes, Route, Navigate } from 'react-router-dom'
import AuthPage from './pages/auth'
import ProtectedRoute from './components/ProtectedRoute'
import DoctorDashboard from './pages/DoctorDashboard'
import PatientDashboard from './pages/PatientDashboard'

function App() {

  return (
    <>
      <Routes>
        <Route path="/" element={<Navigate to="/auth" />} />

        {/* Auth Page */}
        <Route path="/auth" element={<AuthPage />} />

        {/* Doctor Dashboard */}
        <Route
          path="/doctor"
          element={
            <ProtectedRoute allowedRoles={["doctor"]}>
              <DoctorDashboard />
            </ProtectedRoute>
          }
        />

        {/* Patient Dashboard */}
        <Route
          path="/patient"
          element={
            <ProtectedRoute allowedRoles={["patient"]}>
              <PatientDashboard />
            </ProtectedRoute>
          }
        />

        <Route path="*" element={<h2>404 Not Found</h2>} />

      </Routes>
    </>
  )
}

export default App
