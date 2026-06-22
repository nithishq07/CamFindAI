import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Mail, Lock, User, Building2, Eye, EyeOff, ArrowRight, Loader2, AlertCircle } from 'lucide-react';
import { SmokeyBackground } from '../components/auth/SmokeyBackground';
import { FloatingInput } from '../components/auth/FloatingInput';
import { useAuth } from '../contexts/AuthContext';
import { apiClient } from '../api/client';

export function RegisterPage() {
  const [fullName, setFullName] = useState('');
  const [orgName, setOrgName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [termsAccepted, setTermsAccepted] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [validationErrors, setValidationErrors] = useState<any>({});
  
  const navigate = useNavigate();
  const { setUser } = useAuth();

  const getPasswordStrength = (pwd: string) => {
    if (!pwd) return { level: 0, text: '', color: '' };
    if (pwd.length < 8) return { level: 1, text: 'Weak', color: '#EF4444' };
    const hasUpper = /[A-Z]/.test(pwd);
    const hasNum = /[0-9]/.test(pwd);
    const hasSpec = /[^A-Za-z0-9]/.test(pwd);
    
    if (hasUpper && hasNum && hasSpec) return { level: 4, text: 'Strong', color: '#22C55E' };
    if (hasUpper && hasNum) return { level: 3, text: 'Good', color: '#EAB308' };
    return { level: 2, text: 'Fair', color: '#F59E0B' };
  };

  const strength = getPasswordStrength(password);

  const validate = () => {
    let errors: any = {};
    if (!fullName) errors.fullName = 'Name required';
    if (!orgName) errors.orgName = 'Organization required';
    if (!email) {
      errors.email = 'Email required';
    } else if (!/\S+@\S+\.\S+/.test(email)) {
      errors.email = 'Invalid email';
    }
    if (!password) {
      errors.password = 'Password required';
    } else if (password.length < 6) {
      errors.password = 'Min 6 chars';
    }
    if (password !== confirmPassword) {
      errors.confirmPassword = 'Passwords do not match';
    }
    setValidationErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!validate()) return;
    if (!termsAccepted) return;
    
    setLoading(true);
    setError('');
    try {
      const res = await apiClient.post('/auth/register', { 
        adminName: fullName, 
        orgName: orgName, 
        email: email, 
        password: password,
        industry: "Security",
        phone: "0000000000",
        orgSize: "1-10"
      });
      localStorage.setItem('token', res.data.access_token);
      
      // Fetch user profile
      apiClient.defaults.headers.common['Authorization'] = `Bearer ${res.data.access_token}`;
      const meRes = await apiClient.get('/auth/me');
      setUser(meRes.data);
      
      navigate('/');
    } catch (err: any) {
      setError(err.response?.data?.message || 'Registration failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="relative min-h-screen w-full overflow-hidden bg-[#0A0A0A] flex items-center justify-center font-inter">
      <SmokeyBackground />
      <div 
        className="absolute z-10 w-full max-w-[460px] px-8 py-10"
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
          <h1 className="text-xl font-semibold text-[#E2E8F0]">Create your account</h1>
          <p className="text-sm text-[#94A3B8]">Set up your organization on CamFindAI</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-5">
          <div className="grid grid-cols-2 gap-4">
            <FloatingInput
              id="fullName"
              type="text"
              label="Full name"
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              icon={<User size={14} />}
              error={validationErrors.fullName}
            />
            <FloatingInput
              id="orgName"
              type="text"
              label="Organization"
              value={orgName}
              onChange={(e) => setOrgName(e.target.value)}
              icon={<Building2 size={14} />}
              error={validationErrors.orgName}
            />
          </div>

          <FloatingInput
            id="email"
            type="email"
            label="Email address"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            icon={<Mail size={14} />}
            error={validationErrors.email}
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
              error={validationErrors.password}
            />
            <button
              type="button"
              onClick={() => setShowPassword(!showPassword)}
              className="absolute right-0 top-4 text-[#64748B] hover:text-[#E2E8F0] transition-colors"
            >
              {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
            </button>
            {password.length > 0 && (
              <div className="mt-2 flex items-center justify-between">
                <div className="flex gap-1 flex-1 mr-4">
                  {[1, 2, 3, 4].map((seg) => (
                    <div 
                      key={seg} 
                      className={`h-1 flex-1 rounded-full ${seg <= strength.level ? '' : 'bg-[#1E293B]'}`}
                      style={{ backgroundColor: seg <= strength.level ? strength.color : '' }}
                    />
                  ))}
                </div>
                <span className="text-xs font-medium" style={{ color: strength.color }}>
                  {strength.text}
                </span>
              </div>
            )}
          </div>

          <FloatingInput
            id="confirmPassword"
            type={showPassword ? "text" : "password"}
            label="Confirm password"
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            icon={<Lock size={14} />}
            error={validationErrors.confirmPassword}
          />

          <div className="flex items-start gap-2 pt-1">
            <input 
              type="checkbox" 
              id="terms" 
              checked={termsAccepted}
              onChange={(e) => setTermsAccepted(e.target.checked)}
              className="mt-0.5 appearance-none w-4 h-4 rounded border border-[#262626] bg-transparent checked:bg-[#DC2626] checked:border-[#DC2626] transition-colors cursor-pointer flex-shrink-0 flex items-center justify-center after:content-[''] after:w-[3px] after:h-[7px] after:border-r-2 after:border-b-2 after:border-white after:rotate-45 after:-mt-0.5 checked:after:block after:hidden"
            />
            <label htmlFor="terms" className="text-xs text-[#94A3B8] leading-snug cursor-pointer select-none">
              I agree to the <a href="#" className="text-[#DC2626] hover:underline">Terms of Service</a> and <a href="#" className="text-[#DC2626] hover:underline">Privacy Policy</a>
            </label>
          </div>

          <button
            type="submit"
            disabled={loading || !termsAccepted}
            className="group w-full flex items-center justify-center gap-2 bg-[#DC2626] text-white py-2.5 rounded-lg font-semibold transition-all hover:bg-[#B91C1C] hover:-translate-y-px disabled:opacity-50 disabled:hover:translate-y-0 disabled:bg-[#1E293B] disabled:text-[#64748B] disabled:cursor-not-allowed"
          >
            {loading ? (
              <>
                Creating account...
                <Loader2 size={16} className="animate-spin" />
              </>
            ) : (
              <>
                Create Account
                <ArrowRight size={16} className="transition-transform group-hover:translate-x-1" />
              </>
            )}
          </button>

          {error && (
            <p className="text-[#EF4444] text-xs flex items-center gap-1 mt-2">
              <AlertCircle size={12} /> {error}
            </p>
          )}
        </form>

        <div className="mt-8 text-center">
          <span className="text-[#94A3B8] text-xs">Already have an account? </span>
          <button 
            onClick={() => navigate('/login')}
            className="text-[#DC2626] font-medium hover:text-[#B91C1C] text-xs transition-colors"
          >
            Sign in
          </button>
        </div>
      </div>
    </div>
  );
}
