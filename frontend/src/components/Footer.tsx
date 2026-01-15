import React from 'react';
import { Cpu, HardDrive, Info } from 'lucide-react';

interface FooterProps {
  cpu: string;
  ram: string;
  version: string;
}

export const Footer: React.FC<FooterProps> = ({ cpu, ram, version }) => {
  return (
    <div className="w-full px-4 py-2 border-t border-omnix-primary/20 bg-omnix-bg-dark/80 backdrop-blur-md flex items-center justify-between pointer-events-auto">
      <div className="flex items-center gap-6">
        <div className="flex items-center gap-2 text-[10px] font-hud tracking-wider text-omnix-text-secondary">
          <Cpu size={12} className="text-omnix-primary" />
          <span>CPU: <span className="text-omnix-primary">{cpu}</span></span>
        </div>
        <div className="flex items-center gap-2 text-[10px] font-hud tracking-wider text-omnix-text-secondary">
          <HardDrive size={12} className="text-omnix-primary" />
          <span>RAM: <span className="text-omnix-primary">{ram}</span></span>
        </div>
      </div>

      <div className="flex items-center gap-4">
        <div className="flex items-center gap-1.5 text-[10px] font-hud tracking-widest text-omnix-primary/60">
          <Info size={12} />
          <span>OMNIX {version}</span>
        </div>
        <div className="flex gap-1">
          <div className="w-1 h-3 bg-omnix-primary/20" />
          <div className="w-1 h-3 bg-omnix-primary/40" />
          <div className="w-1 h-3 bg-omnix-primary/60" />
        </div>
      </div>
    </div>
  );
};
