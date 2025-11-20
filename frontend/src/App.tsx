import React, { useState } from 'react';
import {
  Settings, Shield, Bell, Lock, Activity,
  MessageSquare, Send, Crosshair, Trophy, Cpu, Layers
} from 'lucide-react';

// Reusable HUD Panel Component
const Panel = ({ children, className = "", title }: { children: React.ReactNode, className?: string, title?: string }) => (
  <div className={`relative bg-omnix-panel border border-omnix-blue/30 rounded-lg p-4 backdrop-blur-md ${className}`}>
    {/* Decorative Corner Accents */}
    <div className="absolute top-0 left-0 w-2 h-2 border-t-2 border-l-2 border-omnix-blue"></div>
    <div className="absolute top-0 right-0 w-2 h-2 border-t-2 border-r-2 border-omnix-blue"></div>
    <div className="absolute bottom-0 left-0 w-2 h-2 border-b-2 border-l-2 border-omnix-blue"></div>
    <div className="absolute bottom-0 right-0 w-2 h-2 border-b-2 border-r-2 border-omnix-blue"></div>

    {title && (
      <h3 className="text-omnix-blue font-hud tracking-widest text-sm mb-4 border-b border-omnix-blue/20 pb-2 flex items-center gap-2">
        {title}
      </h3>
    )}
    {children}
  </div>
);

export default function OmnixHUD() {
  const [activeProvider, setActiveProvider] = useState('hybridnex');

  return (
    <div className="min-h-screen bg-omnix-dark text-omnix-text font-body p-8 flex items-center justify-center bg-[url('https://www.transparenttextures.com/patterns/stardust.png')]">
      {/* Main HUD Container */}
      <div className="w-full max-w-6xl border-2 border-omnix-blue/50 rounded-3xl p-6 relative shadow-neon-blue bg-opacity-90 bg-omnix-dark">

        {/* Header */}
        <header className="mb-8 text-center relative">
          <h1 className="text-6xl font-hud font-black text-transparent bg-clip-text bg-gradient-to-b from-white to-omnix-blue drop-shadow-[0_0_10px_rgba(0,243,255,0.8)]">
            OMNIX
          </h1>
          <p className="text-omnix-blue tracking-[0.5em] text-sm font-bold mt-2 uppercase">
            - All Knowing AI Companion -
          </p>
          <div className="h-[1px] w-1/3 bg-gradient-to-r from-transparent via-omnix-blue to-transparent mx-auto mt-4"></div>
        </header>

        <div className="grid grid-cols-12 gap-6 h-[600px]">

          {/* LEFT COLUMN: Chat */}
          <div className="col-span-3 flex flex-col gap-4">
            <Panel className="flex-1 flex flex-col border-omnix-blue/50">
              <div className="flex-1 overflow-y-auto space-y-4 pr-2">
                {/* AI Message */}
                <div className="bg-omnix-blueDim border-l-2 border-omnix-blue p-3 rounded-r-md">
                  <p className="text-xs text-omnix-blue mb-1 font-bold">OMNIX</p>
                  <p className="text-sm">Hello! Ready to assist with your gameplay.</p>
                </div>
                {/* User Message */}
                <div className="bg-white/5 border-r-2 border-white/30 p-3 rounded-l-md text-right">
                  <p className="text-xs text-gray-400 mb-1 font-bold">USER</p>
                  <p className="text-sm">Hii How can I assist-you?</p>
                </div>
                {/* AI Processing */}
                <div className="bg-omnix-blueDim border-l-2 border-omnix-blue p-3 rounded-r-md animate-pulse">
                  <p className="text-xs text-omnix-blue mb-1 font-bold">SYSTEM</p>
                  <p className="text-sm">Sure, analyzing the game now...</p>
                </div>
              </div>

              {/* Input Area */}
              <div className="mt-4 flex gap-2">
                <input
                  type="text"
                  placeholder="Ask anything..."
                  className="w-full bg-black/50 border border-omnix-blue/30 rounded p-2 text-sm focus:outline-none focus:border-omnix-blue focus:shadow-neon-blue placeholder-gray-600"
                />
                <button className="p-2 bg-omnix-blue/20 border border-omnix-blue text-omnix-blue rounded hover:bg-omnix-blue hover:text-black transition-all">
                  <Send size={16} />
                </button>
              </div>
            </Panel>

            <button className="py-4 border border-omnix-blue rounded text-omnix-blue font-hud tracking-widest hover:bg-omnix-blue/10 hover:shadow-neon-blue transition-all">
              OVERLAY
            </button>
          </div>

          {/* CENTER COLUMN: Status & Visualizer */}
          <div className="col-span-5 flex flex-col items-center justify-center relative">
            {/* Central Circle */}
            <div className="relative w-64 h-64 flex items-center justify-center">
              <div className="absolute inset-0 border-4 border-omnix-blue/20 rounded-full"></div>
              <div className="absolute inset-0 border-t-4 border-omnix-blue rounded-full animate-spin-slow"></div>
              <div className="absolute inset-4 border-2 border-dashed border-omnix-red/50 rounded-full"></div>

              <div className="text-center z-10">
                <p className="text-omnix-blue text-xs tracking-widest mb-2">GAME DETECTED</p>
                <h2 className="text-4xl font-hud text-omnix-red font-bold drop-shadow-[0_0_5px_rgba(255,42,42,0.8)]">CS:GO</h2>
                <div className="mt-2 flex items-center justify-center gap-2">
                  <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                  <span className="text-green-400 text-xs">ONLINE</span>
                </div>
              </div>
            </div>

            {/* Stats Hexagon */}
            <div className="mt-8 w-full grid grid-cols-3 gap-4 text-center">
              <div className="p-2">
                <p className="text-omnix-blue text-xs">K/D</p>
                <p className="text-xl font-bold">1.52</p>
              </div>
              <div className="relative border border-omnix-red/50 p-4 clip-hexagon flex items-center justify-center">
                 <Crosshair className="text-omnix-red w-8 h-8" />
              </div>
              <div className="p-2">
                <p className="text-omnix-blue text-xs">WINS</p>
                <p className="text-xl font-bold">∞</p>
              </div>
            </div>

            {/* Bottom Icons */}
            <div className="mt-8 flex gap-6 text-omnix-red">
               <Activity />
               <Settings className="animate-spin-slow" />
               <Trophy />
            </div>
          </div>

          {/* RIGHT COLUMN: Settings */}
          <div className="col-span-4 flex flex-col gap-4">
            {/* Menu Panel */}
            <Panel title="SETTINGS" className="flex-1">
              <ul className="space-y-4">
                <li className="group cursor-pointer flex items-center justify-between p-2 hover:bg-omnix-blue/10 border border-transparent hover:border-omnix-blue/30 transition-all rounded">
                  <div className="flex items-center gap-3">
                    <Layers size={18} className="text-omnix-blue" />
                    <span>Overlay Mode</span>
                  </div>
                  <div className="w-1 h-1 bg-omnix-blue rounded-full opacity-0 group-hover:opacity-100"></div>
                </li>
                <li className="group cursor-pointer flex items-center justify-between p-2 hover:bg-omnix-blue/10 border border-transparent hover:border-omnix-blue/30 transition-all rounded">
                  <div className="flex items-center gap-3">
                    <Settings size={18} />
                    <span>General</span>
                  </div>
                </li>
                <li className="group cursor-pointer flex items-center justify-between p-2 hover:bg-omnix-blue/10 border border-transparent hover:border-omnix-blue/30 transition-all rounded">
                  <div className="flex items-center gap-3">
                    <Bell size={18} />
                    <span>Notifications</span>
                  </div>
                </li>
                <li className="group cursor-pointer flex items-center justify-between p-2 hover:bg-omnix-blue/10 border border-transparent hover:border-omnix-blue/30 transition-all rounded">
                  <div className="flex items-center gap-3">
                    <Lock size={18} />
                    <span>Privacy</span>
                  </div>
                </li>
              </ul>
            </Panel>

            {/* AI Provider Panel */}
            <Panel title="AI PROVIDER">
              <div className="space-y-3">
                <div
                  onClick={() => setActiveProvider('synapse')}
                  className={`cursor-pointer p-3 border rounded flex items-center gap-4 transition-all ${activeProvider === 'synapse' ? 'border-omnix-blue bg-omnix-blue/10 shadow-neon-blue' : 'border-gray-700 hover:border-gray-500'}`}
                >
                  <div className={`w-4 h-4 rounded-full border flex items-center justify-center ${activeProvider === 'synapse' ? 'border-omnix-blue' : 'border-gray-500'}`}>
                    {activeProvider === 'synapse' && <div className="w-2 h-2 bg-omnix-blue rounded-full"></div>}
                  </div>
                  <span className="font-hud tracking-wider">SYNAPSE</span>
                </div>

                <div
                  onClick={() => setActiveProvider('hybridnex')}
                  className={`cursor-pointer p-3 border rounded flex items-center gap-4 transition-all ${activeProvider === 'hybridnex' ? 'border-omnix-blue bg-omnix-blue/10 shadow-neon-blue' : 'border-gray-700 hover:border-gray-500'}`}
                >
                  <div className={`w-4 h-4 rounded-full border flex items-center justify-center ${activeProvider === 'hybridnex' ? 'border-omnix-blue' : 'border-gray-500'}`}>
                     {activeProvider === 'hybridnex' && <div className="w-2 h-2 bg-omnix-blue rounded-full"></div>}
                  </div>
                  <span className="font-hud tracking-wider">HYBRIDNEX</span>
                </div>
              </div>
            </Panel>

            <button className="py-3 border border-gray-700 rounded text-gray-400 hover:text-white hover:border-white transition-all font-hud tracking-widest">
              SETTINGS
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
