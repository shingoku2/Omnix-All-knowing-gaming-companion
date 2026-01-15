import React, { useState, useEffect } from 'react';
import { MainContainer } from './components/MainContainer';
import { RightSideMenu, MenuItem } from './components/RightSideMenu';
import { ChatModule, Message } from './components/ChatModule';
import { SettingsModule } from './components/SettingsModule';
import { MacrosModule } from './components/MacrosModule';
import { KnowledgeModule } from './components/KnowledgeModule';
import { CentralHUD } from './components/CentralHUD';
import { Footer } from './components/Footer';
import { AnimatedSection } from './components/AnimatedSection';

import { bridge } from './utils/bridge';

const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState('chat');
  const [messages, setMessages] = useState<Message[]>([
    { id: '1', role: 'assistant', content: 'Neural link established. How can I assist you in your current session?' }
  ]);

  // Handle URL parameters for different display modes
  const queryParams = new URLSearchParams(window.location.search);
  const isOverlayMode = queryParams.get('mode') === 'overlay';

  useEffect(() => {
    bridge.setMessageListener((content) => {
      setMessages(prev => [...prev, {
        id: Date.now().toString(),
        role: 'assistant',
        content
      }]);
    });
  }, []);

  const menuItems: MenuItem[] = [
    { id: 'chat', label: 'AI Chat', icon: 'MessageSquare' },
    { id: 'settings', label: 'Settings', icon: 'Settings' },
    { id: 'macros', label: 'Macros', icon: 'Zap' },
    { id: 'knowledge', label: 'Knowledge', icon: 'Library' },
  ];

  const handleSendMessage = (content: string) => {
    const userMsg: Message = { id: Date.now().toString(), role: 'user', content };
    setMessages(prev => [...prev, userMsg]);
    
    // Send to Python backend
    bridge.sendMessage(content);
    
    // Simulate AI response (temporary, until backend pushes back)
    /*
    setTimeout(() => {
      const botMsg: Message = { 
        id: (Date.now() + 1).toString(), 
        role: 'assistant', 
        content: `Analyzing query: "${content}"... Routing through localized neural nodes.` 
      };
      setMessages(prev => [...prev, botMsg]);
    }, 1000);
    */
  };

  // Rendering logic for Overlay Mode
  if (isOverlayMode) {
    return (
      <div className="p-4 flex flex-col items-center gap-4">
        <CentralHUD gameName="Cyberpunk 2077" isDetected={true} />
        <div className="w-[400px] h-[300px]">
          <ChatModule messages={messages} onSendMessage={handleSendMessage} />
        </div>
      </div>
    );
  }

  // Default Dashboard Rendering
  return (
    <div className="min-h-screen bg-omnix-bg-dark flex flex-col items-center justify-center p-4">
      {/* HUD at the top */}
      <div className="mb-8 w-full max-w-5xl flex justify-center">
        <CentralHUD gameName="Cyberpunk 2077" isDetected={true} />
      </div>

      <MainContainer>
        <div className="flex h-[600px] overflow-hidden">
          {/* Main Content Area */}
          <div className="flex-1 p-6 overflow-hidden">
            <AnimatedSection key={activeTab} className="h-full">
              {activeTab === 'chat' && (
                <ChatModule messages={messages} onSendMessage={handleSendMessage} />
              )}
              {activeTab === 'settings' && (
                <SettingsModule />
              )}
              {activeTab === 'macros' && (
                <MacrosModule />
              )}
              {activeTab === 'knowledge' && (
                <KnowledgeModule />
              )}
              {activeTab !== 'chat' && activeTab !== 'settings' && activeTab !== 'macros' && activeTab !== 'knowledge' && (
                <div className="flex items-center justify-center h-full text-omnix-primary/40 font-hud tracking-[0.5em] uppercase">
                  Module Under Development
                </div>
              )}
            </AnimatedSection>
          </div>

          {/* Navigation Sidebar */}
          <RightSideMenu 
            items={menuItems} 
            activeId={activeTab} 
            onSelect={setActiveTab} 
          />
        </div>
        
        <Footer cpu="4.2%" ram="512MB" version="v2.5.0-ALPHA" />
      </MainContainer>
    </div>
  );
};

export default App;