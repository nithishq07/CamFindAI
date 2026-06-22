import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Mail, Lock, Eye, EyeOff, ArrowRight, Loader2, AlertCircle } from 'lucide-react';
import { SmokeyBackground } from '../components/auth/SmokeyBackground';
import { FloatingInput } from '../components/auth/FloatingInput';
import { useAuth } from '../contexts/AuthContext';
import { apiClient } from '../api/client';

export function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [emailError, setEmailError] = useState('');
  const [passwordError, setPasswordError] = useState('');
  const navigate = useNavigate();
  const { setUser } = useAuth();

  const validate = () => {
    let isValid = true;
    setEmailError('');
    setPasswordError('');
    if (!email) {
      setEmailError('Email is required');
      isValid = false;
    } else if (!/\S+@\S+\.\S+/.test(email)) {
      setEmailError('Invalid email format');
      isValid = false;
    }
    if (!password) {
      setPasswordError('Password is required');
      isValid = false;
    } else if (password.length < 6) {
      setPasswordError('Password must be at least 6 characters');
      isValid = false;
    }
    return isValid;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!validate()) return;
    setLoading(true);
    setError('');
    try {
      const res = await apiClient.post('/auth/login', { email, password });
      localStorage.setItem('token', res.data.access_token);
      
      // Fetch user profile
      apiClient.defaults.headers.common['Authorization'] = `Bearer ${res.data.access_token}`;
      const meRes = await apiClient.get('/auth/me');
      setUser(meRes.data);
      
      navigate('/');
    } catch (err: any) {
      setError(err.response?.data?.message || 'Invalid credentials');
    } finally {
      setLoading(false);
    }
  };

  const handleSSO = async (provider: string) => {
    try {
       await apiClient.post(`/auth/sso/${provider}`);
    } catch(err) {
       console.error('SSO failed', err);
    }
  }

  return (
    <div className="relative min-h-screen w-full overflow-hidden bg-[#0A0A0A] flex items-center justify-center font-inter">
      <SmokeyBackground />
      <div 
        className="absolute z-10 w-full max-w-[420px] px-8 py-10"
        style={{
          background: 'rgba(10, 10, 10, 0.75)',
          backdropFilter: 'blur(20px)',
          border: '1px solid rgba(78, 126, 255, 0.15)',
          borderRadius: '16px',
          boxShadow: '0 8px 32px rgba(0, 0, 0, 0.4), 0 0 0 1px rgba(78,126,255,0.05)'
        }}
      >
        <div className="flex flex-col items-center mb-8">
          <div className="font-jetbrains text-2xl font-bold tracking-tight text-[#E2E8F0]">
            CamFind<span className="text-[#DC2626]">AI</span>
          </div>
          <p className="text-xs text-[#64748B] mt-1">Intelligent Surveillance Platform</p>
        </div>

        <div className="mb-6">
          <h1 className="text-xl font-semibold text-[#E2E8F0]">Welcome back</h1>
          <p className="text-sm text-[#94A3B8]">Sign in to your account</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-5">
          <FloatingInput
            id="email"
            type="email"
            label="Email address"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            icon={<Mail size={14} />}
            error={emailError}
            autoComplete="email"
          />

          <div className="relative">
            <FloatingInput
              id="password"
              type={showPassword ? "text" : "password"}
              label="Password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              icon={<Lock size={14} />}
              error={passwordError}
            />
            <button
              type="button"
              onClick={() => setShowPassword(!showPassword)}
              className="absolute right-0 top-4 text-[#64748B] hover:text-[#E2E8F0] transition-colors"
            >
              {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
            </button>
          </div>

          <div className="flex justify-end">
            <a href="#" className="text-xs text-[#DC2626] hover:text-[#B91C1C] transition-colors">
              Forgot password?
            </a>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="group w-full flex items-center justify-center gap-2 bg-[#DC2626] text-white py-2.5 rounded-lg font-semibold transition-all hover:bg-[#B91C1C] hover:-translate-y-px disabled:opacity-70 disabled:hover:translate-y-0"
          >
            {loading ? (
              <>
                Signing in...
                <Loader2 size={16} className="animate-spin" />
              </>
            ) : (
              <>
                Access Platform
                <ArrowRight size={16} className="transition-transform group-hover:translate-x-1" />
              </>
            )}
          </button>

          {error && (
            <p className="text-[#EF4444] text-xs flex items-center gap-1 mt-2">
              <AlertCircle size={12} /> {error}
            </p>
          )}

          <div className="flex items-center gap-4 py-2 mx-4">
            <div className="flex-1 border-t border-[#1E293B]"></div>
            <span className="text-[10px] text-[#64748B] tracking-widest uppercase">Or continue with</span>
            <div className="flex-1 border-t border-[#1E293B]"></div>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <button
              type="button"
              onClick={() => handleSSO('microsoft')}
              className="flex items-center justify-center gap-2 bg-white/5 hover:bg-white/10 border border-[#1E293B] hover:border-[#262626] text-[#E2E8F0] text-sm font-medium rounded-lg py-2.5 transition-colors"
            >
              <svg className="w-4 h-4 text-white" viewBox="0 0 24 24" fill="currentColor">
                <path d="M11.4 24H0V12.6h11.4V24zM24 24H12.6V12.6H24V24zM11.4 11.4H0V0h11.4v11.4zm12.6 0H12.6V0H24v11.4z"/>
              </svg>
              Microsoft
            </button>
            <button
              type="button"
              onClick={() => handleSSO('google')}
              className="flex items-center justify-center gap-2 bg-white/5 hover:bg-white/10 border border-[#1E293B] hover:border-[#262626] text-[#E2E8F0] text-sm font-medium rounded-lg py-2.5 transition-colors"
            >
              <svg className="w-4 h-4" viewBox="0 0 24 24" fill="currentColor">
                <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4"/>
                <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/>
                <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" fill="#FBBC05"/>
                <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335"/>
              </svg>
              Google
            </button>
          </div>
        </form>

        <div className="mt-8 text-center">
          <span className="text-[#94A3B8] text-xs">Don't have an account? </span>
          <button 
            onClick={() => navigate('/register')}
            className="text-[#DC2626] font-medium hover:text-[#B91C1C] text-xs transition-colors"
          >
            Create account
          </button>
        </div>
      </div>
    </div>
  );
}
