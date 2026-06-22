import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Camera, Map, UserPlus, Server, CheckCircle2 } from 'lucide-react';
import clsx from 'clsx';

export function SetupWizard() {
  const navigate = useNavigate();
  const [currentStep, setCurrentStep] = useState(1);

  const [threshold, setThreshold] = useState(0.85);

  const steps = [
    { id: 1, title: 'Add Cameras', icon: Camera, desc: 'Connect RTSP feeds to the intelligence platform.' },
    { id: 2, title: 'Configure Detection Zones', icon: Map, desc: 'Map out restricted areas and alerts.' },
    { id: 3, title: 'Configure ReID Threshold', icon: Server, desc: 'Set the minimum similarity score for matching.' },
    { id: 4, title: 'Invite Team Members', icon: UserPlus, desc: 'Add security operators and investigators.' },
    { id: 5, title: 'Launch CamFindAI', icon: CheckCircle2, desc: 'Initialize the system and go live.' }
  ];

  const handleNext = () => {
    if (currentStep < 5) {
      setCurrentStep(curr => curr + 1);
    } else {
      navigate('/');
    }
  };

  return (
    <div className="min-h-screen bg-bg-base flex flex-col items-center justify-center p-6">
      <div className="w-full max-w-3xl glass-panel p-10 rounded-2xl border-border-subtle relative overflow-hidden bg-bg-surface">
        <div className="text-center mb-12">
          <h1 className="text-3xl font-heading font-bold text-text-primary mb-2">Platform Initialization</h1>
          <p className="text-text-secondary">Complete the mandatory security setup to activate your workspace.</p>
        </div>

        <div className="relative">
          {/* Progress Line */}
          <div className="absolute left-6 top-10 bottom-10 w-0.5 bg-border-subtle" />

          <div className="space-y-8">
            {steps.map((step) => {
              const Icon = step.icon;
              const isActive = currentStep === step.id;
              const isPast = currentStep > step.id;

              return (
                <div key={step.id} className={clsx(
                  "relative flex items-start gap-6 transition-opacity duration-300",
                  isActive ? "opacity-100" : (isPast ? "opacity-50" : "opacity-30")
                )}>
                  <div className={clsx(
                    "relative z-10 w-12 h-12 rounded-full flex items-center justify-center border-2 transition-colors duration-300 bg-bg-surface",
                    isActive ? "border-accent-steel text-accent-steel shadow-[0_0_15px_rgba(59,130,246,0.3)]" : (isPast ? "border-status-success text-status-success" : "border-border-subtle text-text-muted")
                  )}>
                    <Icon className="w-5 h-5" />
                  </div>
                  <div className="pt-2">
                    <h3 className={clsx("text-lg font-heading font-bold", isActive ? "text-text-primary" : "text-text-secondary")}>
                      Step {step.id}: {step.title}
                    </h3>
                    <p className="text-sm text-text-muted mt-1">{step.desc}</p>
                    
                    {isActive && step.id === 3 && (
                      <div className="mt-4 flex items-center gap-3">
                        <label className="text-sm text-text-secondary">Threshold (0.0 - 1.0):</label>
                        <input 
                          type="number" 
                          step="0.01" 
                          min="0" 
                          max="1" 
                          value={threshold}
                          onChange={(e) => setThreshold(parseFloat(e.target.value))}
                          className="bg-bg-base border border-border-subtle rounded px-3 py-1.5 text-white w-24 text-sm"
                        />
                      </div>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        <div className="mt-12 flex justify-end pt-6 border-t border-border-subtle">
          <button 
            onClick={handleNext}
            className="px-8 py-3 bg-accent-steel hover:bg-accent-steel/90 text-white font-medium rounded-md transition-colors"
          >
            {currentStep === 5 ? 'Launch Platform' : 'Continue Setup'}
          </button>
        </div>
      </div>
    </div>
  );
}
