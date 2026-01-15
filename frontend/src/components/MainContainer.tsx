import React from 'react';

interface MainContainerProps {
  children: React.ReactNode;
}

export const MainContainer: React.FC<MainContainerProps> = ({ children }) => {
  return (
    <div 
      data-testid="main-container"
      className="omni-frame w-full h-full max-w-5xl max-h-[80vh] flex flex-col overflow-hidden relative"
    >
      {/* Decorative corner elements could go here */}
      <div className="flex-1 p-6 overflow-auto">
        {children}
      </div>
    </div>
  );
};
