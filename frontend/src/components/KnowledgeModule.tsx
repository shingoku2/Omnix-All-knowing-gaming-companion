import React from 'react';
import { Library, Book, Globe, Search } from 'lucide-react';

export const KnowledgeModule: React.FC = () => {
  const docs = [
    { title: 'Cyberpunk 2077 Wiki', type: 'Web', date: '2026-01-12' },
    { title: 'Advanced Mechanics.pdf', type: 'PDF', date: '2025-12-20' },
    { title: 'Global Strategy Guide', type: 'Local', date: '2026-01-05' },
  ];

  return (
    <div className="flex flex-col h-full space-y-6">
      <div className="flex items-center gap-3 border-b border-omnix-primary/20 pb-4">
        <Library className="text-omnix-primary" size={24} />
        <h2 className="text-xl font-hud tracking-wider text-omnix-primary uppercase">Knowledge Base</h2>
      </div>

      <div className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-omnix-primary/60" size={16} />
        <input 
          type="text" 
          placeholder="SEARCH INTEL..." 
          className="w-full bg-omnix-bg-dark border border-omnix-primary/30 rounded-lg py-2 pl-10 pr-4 text-xs font-hud tracking-wider text-omnix-primary focus:outline-none focus:border-omnix-primary transition-colors"
        />
      </div>

      <div className="flex-1 overflow-y-auto space-y-2 pr-1">
        {docs.map((doc) => (
          <div key={doc.title} className="p-3 flex items-center justify-between group hover:bg-omnix-primary/5 border border-transparent hover:border-omnix-primary/20 rounded-md transition-all cursor-pointer">
            <div className="flex items-center gap-3">
              <Book size={18} className="text-omnix-primary/60 group-hover:text-omnix-primary" />
              <div>
                <p className="text-sm text-omnix-text-primary group-hover:omni-text-glow transition-all">{doc.title}</p>
                <p className="text-[10px] text-omnix-text-secondary uppercase tracking-tighter">{doc.type} • {doc.date}</p>
              </div>
            </div>
            <Globe size={14} className="text-omnix-primary/40" />
          </div>
        ))}
      </div>
    </div>
  );
};
