import React from 'react';
import * as Icons from 'lucide-react';

export interface MenuItem {
  id: string;
  label: string;
  icon: keyof typeof Icons;
}

interface RightSideMenuProps {
  items: MenuItem[];
  activeId: string;
  onSelect: (id: string) => void;
}

export const RightSideMenu: React.FC<RightSideMenuProps> = ({ items, activeId, onSelect }) => {
  return (
    <div className="w-16 h-full flex flex-col items-center py-6 gap-6 bg-omnix-bg-panel/50 border-l border-omnix-primary/20 backdrop-blur-sm">
      {items.map((item) => {
        const IconComponent = Icons[item.icon] as React.ElementType;
        const isActive = activeId === item.id;

        return (
          <button
            key={item.id}
            onClick={() => onSelect(item.id)}
            className={`
              relative group p-2 rounded-lg transition-all duration-300
              ${isActive ? 'text-omnix-primary' : 'text-omnix-text-secondary hover:text-omnix-primary/70'}
            `}
            title={item.label}
          >
            {/* Active Indicator Bar */}
            {isActive && (
              <div className="absolute -right-0.5 top-1/2 -translate-y-1/2 w-1 h-8 bg-omnix-primary omni-glow rounded-l-full" />
            )}

            <div className={`
              transition-transform duration-300 group-hover:scale-110
              ${isActive ? 'omni-text-glow scale-110' : ''}
            `}>
              {IconComponent && <IconComponent size={24} />}
            </div>

            {/* Hover Tooltip (Simplified) */}
            <span className="absolute right-full mr-4 px-2 py-1 rounded bg-omnix-bg-dark border border-omnix-primary/30 text-xs text-omnix-primary opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none whitespace-nowrap">
              {item.label}
            </span>
          </button>
        );
      })}
    </div>
  );
};
