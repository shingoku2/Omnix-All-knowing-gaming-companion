import React from 'react';
import { Target, Activity } from 'lucide-react';

interface CentralHUDProps {
  gameName: string;
  isDetected: boolean;
}

export const CentralHUD: React.FC<CentralHUDProps> = ({ gameName, isDetected }) => {
  return (
    <div className="flex flex-col items-center gap-2 pointer-events-none">
      <div className={`
        px-6 py-2 rounded-t-xl border-t border-x backdrop-blur-md flex items-center gap-4
        ${isDetected ? 'border-omnix-primary/40 bg-omnix-primary/10' : 'border-omnix-secondary/40 bg-omnix-secondary/10'}
      `}>
        <div className="flex items-center gap-2">
          {isDetected ? (
            <Activity size={16} className="text-omnix-primary animate-pulse" />
          ) : (
            <Target size={16} className="text-omnix-secondary animate-spin-slow" />
          )}
          <span className={`text-xs font-hud tracking-widest uppercase ${isDetected ? 'text-omnix-primary' : 'text-omnix-secondary'}`}>
            {isDetected ? 'System Active' : 'Searching for Target'}
          </span>
        </div>
        
        {isDetected && (
          <div className="h-4 w-px bg-omnix-primary/30" />
        )}
        
        {isDetected && (
          <span className="text-sm font-hud font-bold text-omnix-text-primary tracking-tighter">
            {gameName}
          </span>
        )}
      </div>
      
      {/* Decorative scanline bar */}
      <div className={`w-full h-0.5 omni-glow ${isDetected ? 'bg-omnix-primary' : 'bg-omnix-secondary animate-pulse'}`} />
    </div>
  );
};
