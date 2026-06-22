import React from 'react';
import { AlertCircle } from 'lucide-react';

interface FloatingInputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  id: string;
  label: string;
  icon?: React.ReactNode;
  error?: string;
}

export const FloatingInput = React.forwardRef<HTMLInputElement, FloatingInputProps>(
  ({ id, label, icon, error, className = '', ...props }, ref) => {
    return (
      <div className="relative z-0 w-full">
        <input
          id={id}
          ref={ref}
          placeholder=" "
          className={`peer block w-full bg-transparent border-0 border-b border-[rgba(148,163,184,0.25)] pt-5 pb-1 px-0 text-sm text-[#E2E8F0] appearance-none focus:outline-none focus:ring-0 focus:border-[#DC2626] transition-colors duration-200 ${className}`}
          {...props}
        />
        <label
          htmlFor={id}
          className="absolute top-4 left-0 flex items-center gap-1.5 text-sm text-[#64748B] duration-200 transform origin-[0] peer-focus:-translate-y-4 peer-focus:scale-75 peer-focus:text-[#DC2626] peer-[:not(:placeholder-shown)]:-translate-y-4 peer-[:not(:placeholder-shown)]:scale-75 pointer-events-none"
        >
          {icon && <span className="text-current">{icon}</span>}
          {label}
        </label>
        {error && (
          <p className="mt-1 text-xs text-[#EF4444] flex items-center gap-1">
            <AlertCircle size={11} /> {error}
          </p>
        )}
      </div>
    );
  }
);

FloatingInput.displayName = 'FloatingInput';
