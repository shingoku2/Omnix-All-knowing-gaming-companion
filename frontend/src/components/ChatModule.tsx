import React, { useState, useRef, useEffect } from 'react';
import { Send, Bot, User } from 'lucide-react';

export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
}

interface ChatModuleProps {
  messages: Message[];
  onSendMessage: (content: string) => void;
}

export const ChatModule: React.FC<ChatModuleProps> = ({ messages, onSendMessage }) => {
  const [inputValue, setInputValue] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    if (typeof messagesEndRef.current?.scrollIntoView === 'function') {
      messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (inputValue.trim()) {
      onSendMessage(inputValue.trim());
      setInputValue('');
    }
  };

  return (
    <div 
      data-testid="chat-module"
      className="omni-frame flex flex-col h-full overflow-hidden"
    >
      {/* Header */}
      <div className="px-4 py-3 border-b border-omnix-primary/20 bg-omnix-primary/5 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Bot size={18} className="text-omnix-primary" />
          <span className="text-sm font-hud tracking-wider text-omnix-primary uppercase">Neural Assistant</span>
        </div>
        <div className="w-2 h-2 rounded-full bg-omnix-primary animate-pulse" />
      </div>

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4 scrollbar-thin scrollbar-thumb-omnix-primary/20">
        {messages.map((msg) => (
          <div 
            key={msg.id} 
            className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div className={`
              max-w-[85%] flex gap-3 
              ${msg.role === 'user' ? 'flex-row-reverse' : 'flex-row'}
            `}>
              <div className={`
                flex-shrink-0 w-8 h-8 rounded-lg flex items-center justify-center border
                ${msg.role === 'user' ? 'border-omnix-secondary/30 bg-omnix-secondary/10' : 'border-omnix-primary/30 bg-omnix-primary/10'}
              `}>
                {msg.role === 'user' ? <User size={16} className="text-omnix-secondary" /> : <Bot size={16} className="text-omnix-primary" />}
              </div>
              
              <div className={`
                p-3 rounded-2xl text-sm leading-relaxed
                ${msg.role === 'user' 
                  ? 'bg-omnix-secondary/5 border border-omnix-secondary/20 text-omnix-text-primary rounded-tr-none' 
                  : 'bg-omnix-primary/5 border border-omnix-primary/20 text-omnix-text-primary rounded-tl-none'}
              `}>
                {msg.content}
              </div>
            </div>
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <form 
        onSubmit={handleSubmit}
        className="p-4 border-t border-omnix-primary/20 bg-omnix-bg-dark/40"
      >
        <div className="relative group">
          <input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            placeholder="Type your message..."
            className="w-full bg-omnix-bg-dark border border-omnix-primary/30 rounded-lg py-3 px-4 pr-12 text-sm text-omnix-text-primary focus:outline-none focus:border-omnix-primary transition-colors placeholder-omnix-text-secondary/50"
          />
          <button
            type="submit"
            disabled={!inputValue.trim()}
            className="absolute right-2 top-1/2 -translate-y-1/2 p-2 text-omnix-primary hover:text-white disabled:text-omnix-primary/20 transition-colors"
          >
            <Send size={20} className={inputValue.trim() ? 'omni-text-glow' : ''} />
          </button>
          
          {/* Input Decoration Line */}
          <div className="absolute bottom-0 left-1/2 -translate-x-1/2 w-0 h-0.5 bg-omnix-primary group-focus-within:w-full transition-all duration-300" />
        </div>
      </form>
    </div>
  );
};
