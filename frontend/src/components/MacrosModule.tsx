import React from 'react';
import { Zap, Save } from 'lucide-react';

export const MacrosModule: React.FC = () => {
  const macros = [
    { name: 'Rapid Fire', bind: 'M1', active: true },
    { name: 'Quick Scope', bind: 'Q', active: false },
    { name: 'Auto Run', bind: 'V', active: true },
  ];

  return (
    <div className="flex flex-col h-full space-y-6">
      <div className="flex items-center gap-3 border-b border-omnix-primary/20 pb-4">
        <Zap className="text-omnix-primary" size={24} />
        <h2 className="text-xl font-hud tracking-wider text-omnix-primary uppercase">Macro Automation</h2>
      </div>

      <div className="space-y-3">
        {macros.map((macro) => (
          <div key={macro.name} className="flex items-center justify-between p-4 rounded-lg bg-omnix-primary/5 border border-omnix-primary/10">
            <div className="flex items-center gap-4">
              <div className={`w-2 h-2 rounded-full ${macro.active ? 'bg-omnix-primary omni-glow' : 'bg-omnix-text-secondary'}`} />
              <div>
                <p className="text-sm font-hud text-omnix-text-primary tracking-tight">{macro.name}</p>
                <p className="text-[10px] text-omnix-primary/60 font-mono">BIND: {macro.bind}</p>
              </div>
            </div>
            <button className={`px-3 py-1 rounded text-[10px] font-hud tracking-widest uppercase border transition-colors ${
              macro.active ? 'border-omnix-primary text-omnix-primary bg-omnix-primary/10' : 'border-omnix-text-secondary/30 text-omnix-text-secondary'
            }`}>
              {macro.active ? 'Active' : 'Standby'}
            </button>
          </div>
        ))}
      </div>

      <button className="mt-auto w-full py-3 flex items-center justify-center gap-2 border border-omnix-primary/40 bg-omnix-primary/10 text-omnix-primary font-hud tracking-widest uppercase hover:bg-omnix-primary/20 transition-all">
        <Save size={16} />
        Create New Macro
      </button>
    </div>
  );
};
