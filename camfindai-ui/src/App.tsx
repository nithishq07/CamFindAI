import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Layout } from './components/Layout';
import { LiveView } from './pages/LiveView';
import { Identities } from './pages/Identities';
import { Alerts } from './pages/Alerts';
import { LoginPage } from './pages/LoginPage';
import { RegisterPage } from './pages/RegisterPage';
import { SetupWizard } from './pages/SetupWizard';
import { CameraManagement } from './pages/CameraManagement';
import { Timeline } from './pages/Timeline';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import { GuestRoute } from './components/auth/GuestRoute';

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { user, loading } = useAuth();
  
  if (loading) {
    return <div className="flex h-screen items-center justify-center bg-background text-white">Loading...</div>;
  }
  
  if (!user) {
    return <Navigate to="/login" replace />;
  }
  return <>{children}</>;
}

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<GuestRoute><LoginPage /></GuestRoute>} />
          <Route path="/register" element={<GuestRoute><RegisterPage /></GuestRoute>} />
          <Route path="/setup" element={<SetupWizard />} />
          <Route path="/" element={<ProtectedRoute><Layout /></ProtectedRoute>}>
            <Route index element={<LiveView />} />
            <Route path="identities" element={<Identities />} />
            <Route path="alerts" element={<Alerts />} />
            <Route path="cameras" element={<CameraManagement />} />
            <Route path="timeline" element={<Timeline />} />
            <Route path="*" element={<div className="text-white">Under Construction</div>} />
          </Route>
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;
