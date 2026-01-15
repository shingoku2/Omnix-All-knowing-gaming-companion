import React from 'react';
import { Settings, Shield, Bell, Monitor } from 'lucide-react';

export const SettingsModule: React.FC = () => {
  return (
    <div className="flex flex-col h-full space-y-6">
      <div className="flex items-center gap-3 border-b border-omnix-primary/20 pb-4">
        <Settings className="text-omnix-primary" size={24} />
        <h2 className="text-xl font-hud tracking-wider text-omnix-primary uppercase">System Configuration</h2>
      </div>

      <div className="grid grid-cols-2 gap-4">
        {[
          { icon: Monitor, label: 'Overlay', desc: 'HUD position and scale' },
          { icon: Shield, label: 'Security', desc: 'API keys and privacy' },
          { icon: Bell, label: 'Alerts', desc: 'Notification settings' },
          { icon: Settings, label: 'Advanced', desc: 'Neural core parameters' },
        ].map((item) => (
          <div key={item.label} className="p-4 rounded-lg bg-omnix-primary/5 border border-omnix-primary/10 hover:border-omnix-primary/30 transition-colors cursor-pointer group">
            <div className="flex items-center gap-3 mb-2">
              <item.icon size={18} className="text-omnix-primary group-hover:omni-text-glow" />
              <span className="font-hud text-sm tracking-tighter text-omnix-text-primary">{item.label}</span>
            </div>
            <p className="text-xs text-omnix-text-secondary">{item.desc}</p>
          </div>
        ))}
      </div>
    </div>
  );
};
