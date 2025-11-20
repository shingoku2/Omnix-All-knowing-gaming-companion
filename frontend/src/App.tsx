import React, { useMemo, useState } from 'react';
import {
  Lock,
  Activity,
  Crosshair,
  Cpu,
  ChevronRight,
  Circle,
  Bell,
  ShieldCheck,
  MonitorSmartphone,
  SunMoon,
  MessageSquare,
  RefreshCw,
  Power
} from 'lucide-react';

// Geometric Corner Brackets Component
const CornerBrackets = () => (
  <>
    {/* Top Left */}
    <div className="absolute -top-[1px] -left-[1px] w-12 h-12">
      <div className="absolute top-0 left-0 w-full h-[2px] bg-gradient-to-r from-omnix-blue to-transparent"></div>
      <div className="absolute top-0 left-0 w-[2px] h-full bg-gradient-to-b from-omnix-blue to-transparent"></div>
      <div className="absolute top-2 left-2 w-3 h-[2px] bg-omnix-blue/50"></div>
      <div className="absolute top-2 left-2 w-[2px] h-3 bg-omnix-blue/50"></div>
    </div>
    {/* Top Right */}
    <div className="absolute -top-[1px] -right-[1px] w-12 h-12">
      <div className="absolute top-0 right-0 w-full h-[2px] bg-gradient-to-l from-omnix-blue to-transparent"></div>
      <div className="absolute top-0 right-0 w-[2px] h-full bg-gradient-to-b from-omnix-blue to-transparent"></div>
      <div className="absolute top-2 right-2 w-3 h-[2px] bg-omnix-blue/50"></div>
      <div className="absolute top-2 right-2 w-[2px] h-3 bg-omnix-blue/50"></div>
    </div>
    {/* Bottom Left */}
    <div className="absolute -bottom-[1px] -left-[1px] w-12 h-12">
      <div className="absolute bottom-0 left-0 w-full h-[2px] bg-gradient-to-r from-omnix-blue to-transparent"></div>
      <div className="absolute bottom-0 left-0 w-[2px] h-full bg-gradient-to-t from-omnix-blue to-transparent"></div>
      <div className="absolute bottom-2 left-2 w-3 h-[2px] bg-omnix-blue/50"></div>
      <div className="absolute bottom-2 left-2 w-[2px] h-3 bg-omnix-blue/50"></div>
    </div>
    {/* Bottom Right */}
    <div className="absolute -bottom-[1px] -right-[1px] w-12 h-12">
      <div className="absolute bottom-0 right-0 w-full h-[2px] bg-gradient-to-l from-omnix-blue to-transparent"></div>
      <div className="absolute bottom-0 right-0 w-[2px] h-full bg-gradient-to-t from-omnix-blue to-transparent"></div>
      <div className="absolute bottom-2 right-2 w-3 h-[2px] bg-omnix-blue/50"></div>
      <div className="absolute bottom-2 right-2 w-[2px] h-3 bg-omnix-blue/50"></div>
    </div>
  </>
);

type PanelProps = {
  children: React.ReactNode;
  className?: string;
  title?: string;
  footer?: string;
};

const Panel = ({ children, className = "", title, footer }: PanelProps) => (
  <div className={`relative bg-omnix-panel border border-omnix-blue/20 rounded-sm p-6 backdrop-blur-md ${className}`}>
    <CornerBrackets />

    {title && (
      <h3 className="text-omnix-blue font-hud tracking-[0.3em] text-xs mb-6 uppercase">
        {title}
      </h3>
    )}
    {children}
    {footer && (
      <div className="mt-6 pt-4 border-t border-omnix-blue/10">
        <p className="text-center text-omnix-blue/50 font-hud tracking-[0.3em] text-xs uppercase">
          {footer}
        </p>
      </div>
    )}
  </div>
);

type ChatMessage = {
  id: number;
  author: 'omnix' | 'user';
  text: string;
  status?: 'processing' | 'reply';
};

export default function OmnixHUD() {
  const [activeProvider, setActiveProvider] = useState('hybridnex');
  const [activeSetting, setActiveSetting] = useState<'overlay' | 'general' | 'notifications' | 'privacy'>('overlay');
  const [overlayMode, setOverlayMode] = useState<'compact' | 'immersive'>('immersive');
  const [lockPosition, setLockPosition] = useState(true);
  const [generalSettings, setGeneralSettings] = useState({ autoStart: true, energySaver: false, showTooltips: true });
  const [notificationSettings, setNotificationSettings] = useState({ desktop: true, sound: false, aiUpdates: true });
  const [privacySettings, setPrivacySettings] = useState({ streamerMode: true, redactLogs: true, shareUsage: false });
  const [messages, setMessages] = useState<ChatMessage[]>([
    { id: 1, author: 'omnix', text: 'Hello! I am monitoring your current match.' },
    { id: 2, author: 'user', text: 'Hi! How can you assist me?' },
    { id: 3, author: 'omnix', text: 'Analyzing the game now...', status: 'processing' }
  ]);
  const [chatInput, setChatInput] = useState('');

  const settingsMenu = useMemo(
    () => [
      { id: 'overlay' as const, label: 'Overlay Mode', icon: MonitorSmartphone },
      { id: 'general' as const, label: 'General', icon: SunMoon },
      { id: 'notifications' as const, label: 'Notifications', icon: Bell },
      { id: 'privacy' as const, label: 'Privacy', icon: ShieldCheck }
    ],
    []
  );

  const appendMessage = (text: string) => {
    const trimmed = text.trim();
    if (!trimmed) return;

    setMessages(prev => {
      const nextId = prev[prev.length - 1]?.id ? prev[prev.length - 1].id + 1 : 1;
      const userMessage: ChatMessage = { id: nextId, author: 'user', text: trimmed };
      const acknowledgment: ChatMessage = {
        id: nextId + 1,
        author: 'omnix',
        text: `Routing to ${activeProvider.toUpperCase()}...`,
        status: 'reply'
      };

      return [...prev, userMessage, acknowledgment];
    });

    setChatInput('');
  };

  const toggleSetting = (group: 'general' | 'notifications' | 'privacy', key: string) => {
    const updateMap = {
      general: setGeneralSettings,
      notifications: setNotificationSettings,
      privacy: setPrivacySettings
    } as const;

    updateMap[group](prev => ({ ...prev, [key]: !prev[key as keyof typeof prev] }));
  };

  return (
    <div className="min-h-screen bg-omnix-dark text-omnix-text font-body p-8 flex items-center justify-center bg-[url('https://www.transparenttextures.com/patterns/stardust.png')]">
      {/* Main HUD Container */}
      <div className="w-full max-w-7xl relative">
        <div className="relative border border-omnix-blue/30 rounded-sm p-8 bg-omnix-dark/95 backdrop-blur-lg">
          <CornerBrackets />

          {/* Header */}
          <header className="mb-10 relative">
            <div className="flex items-center gap-4">
              {/* Left decorative line */}
              <div className="flex-1 flex items-center gap-1">
                <div className="h-[2px] flex-1 bg-gradient-to-r from-transparent via-omnix-blue/50 to-omnix-blue"></div>
                <div className="w-2 h-2 border border-omnix-blue rotate-45"></div>
                <div className="w-1 h-1 bg-omnix-blue"></div>
              </div>

              {/* Logo */}
              <div className="text-center">
                <h1 className="text-7xl font-hud font-black tracking-wider">
                  <span className="text-transparent bg-clip-text bg-gradient-to-b from-white via-omnix-blue to-omnix-blue drop-shadow-[0_0_20px_rgba(0,243,255,0.8)]">
                    OMNIX
                  </span>
                </h1>
                <p className="text-omnix-blue tracking-[0.4em] text-xs font-hud mt-2 uppercase opacity-80">
                  - All Knowing AI Companion -
                </p>
              </div>

              {/* Right decorative line */}
              <div className="flex-1 flex items-center gap-1">
                <div className="w-1 h-1 bg-omnix-blue"></div>
                <div className="w-2 h-2 border border-omnix-blue rotate-45"></div>
                <div className="h-[2px] flex-1 bg-gradient-to-l from-transparent via-omnix-blue/50 to-omnix-blue"></div>
              </div>
            </div>
          </header>

        <div className="grid grid-cols-12 gap-6 h-[600px]">

          {/* LEFT COLUMN: Chat/Overlay */}
          <div className="col-span-3 flex flex-col">
            <Panel className="flex-1 flex flex-col" footer="OVERLAY">
              <div className="flex-1 overflow-y-auto space-y-3 pr-2">
                {messages.map(message => (
                  <div
                    key={message.id}
                    className={`p-3 rounded-sm border-l-2 ${
                      message.author === 'omnix'
                        ? 'bg-omnix-blueDim/50 border-omnix-blue'
                        : 'bg-white/5 border-white/30'
                    }`}
                  >
                    <div className="flex items-center gap-2">
                      {message.author === 'omnix' ? (
                        <MessageSquare className="w-4 h-4 text-omnix-blue" />
                      ) : (
                        <Circle className="w-3 h-3 text-omnix-blue/70" />
                      )}
                      <p className="text-sm text-omnix-text">
                        {message.text}
                      </p>
                    </div>
                    {message.status === 'processing' && (
                      <div className="flex items-center gap-3 mt-2 text-omnix-blue text-xs">
                        <div className="relative w-6 h-6">
                          <div className="absolute inset-0 border-2 border-omnix-blue/20 rounded-full"></div>
                          <div className="absolute inset-0 border-t-2 border-omnix-blue rounded-full animate-spin"></div>
                        </div>
                        Analyzing the game now...
                      </div>
                    )}
                  </div>
                ))}
              </div>

              <div className="mt-4 space-y-3">
                <div className="flex gap-2">
                  <input
                    value={chatInput}
                    onChange={e => setChatInput(e.target.value)}
                    onKeyDown={e => e.key === 'Enter' && appendMessage(chatInput)}
                    placeholder="Type a command or ask for guidance..."
                    className="flex-1 bg-omnix-dark/70 border border-omnix-blue/30 rounded-sm px-3 py-2 text-sm focus:outline-none focus:border-omnix-blue text-omnix-text"
                  />
                  <button
                    onClick={() => appendMessage(chatInput)}
                    className="px-4 py-2 bg-omnix-blue/20 border border-omnix-blue/60 text-omnix-blue font-hud tracking-[0.2em] text-xs uppercase hover:bg-omnix-blue/30 transition-colors"
                  >
                    Send
                  </button>
                </div>

                <div className="grid grid-cols-2 gap-2">
                  {[
                    { label: 'Ask for strategy', text: 'Give me a quick strat for this round.' },
                    { label: 'Request macro', text: 'Prepare a recoil-control macro.' },
                    { label: 'Status check', text: 'Are overlays locked in place?' },
                    { label: 'Provider switch', text: `Confirm ${activeProvider.toUpperCase()} routing.` }
                  ].map(action => (
                    <button
                      key={action.label}
                      onClick={() => appendMessage(action.text)}
                      className="text-left px-3 py-2 border border-omnix-blue/20 hover:border-omnix-blue/40 hover:bg-omnix-blue/5 text-xs text-omnix-text rounded-sm transition-all"
                    >
                      {action.label}
                    </button>
                  ))}
                </div>
              </div>
            </Panel>
          </div>

          {/* CENTER COLUMN: Game Detection */}
          <div className="col-span-5 flex flex-col items-center justify-center relative gap-8">
            {/* Hexagonal Frame */}
            <div className="relative">
              {/* Outer hexagonal border */}
              <div className="relative w-72 h-72 flex items-center justify-center">
                <div className="absolute inset-0 clip-hexagon-border border-2 border-omnix-blue/40"></div>

                {/* Animated rotating ring */}
                <div className="absolute inset-3">
                  <div className="absolute inset-0 border-2 border-omnix-blue/20 rounded-full"></div>
                  <div className="absolute inset-0 border-t-2 border-omnix-blue rounded-full animate-spin-slow"></div>
                </div>

                {/* Inner content circle */}
                <div className="relative w-48 h-48 rounded-full border-2 border-omnix-blue/30 flex items-center justify-center bg-omnix-panel">
                  <div className="text-center z-10">
                    {/* CS:GO Icon placeholder */}
                    <div className="mx-auto w-20 h-20 mb-3 flex items-center justify-center">
                      <Crosshair className="w-full h-full text-omnix-red drop-shadow-[0_0_10px_rgba(255,42,42,0.6)]" />
                    </div>
                  </div>
                </div>

                {/* Top label */}
                <div className="absolute -top-6 left-1/2 transform -translate-x-1/2">
                  <div className="relative px-4 py-1 bg-omnix-dark border-l border-r border-omnix-blue/40">
                    <p className="text-omnix-blue text-xs tracking-[0.3em] font-hud uppercase">Game Detected</p>
                    <div className="absolute -top-1 left-0 w-full h-[2px] bg-gradient-to-r from-transparent via-omnix-blue/60 to-transparent"></div>
                  </div>
                </div>

                {/* Bottom status */}
                <div className="absolute -bottom-8 left-1/2 transform -translate-x-1/2 flex items-center gap-2">
                  <Circle className="w-2 h-2 text-green-500 fill-green-500 animate-pulse" />
                  <span className="text-green-400 text-xs tracking-widest uppercase">Online</span>
                </div>
              </div>
            </div>

            {/* Stats Row */}
            <div className="w-full flex items-center justify-center gap-8">
              {/* K/D Stat */}
              <div className="text-center">
                <p className="text-omnix-blue text-xs tracking-wider font-hud mb-1 uppercase">K/D</p>
                <p className="text-2xl font-bold text-omnix-text">1.52</p>
              </div>

              {/* Center Hexagon Icon */}
              <div className="relative w-16 h-16">
                <div className="absolute inset-0 clip-hexagon border-2 border-omnix-red/60 bg-omnix-red/10 flex items-center justify-center">
                  <Crosshair className="w-6 h-6 text-omnix-red" />
                </div>
              </div>

              {/* Wins Stat */}
              <div className="text-center">
                <p className="text-omnix-blue text-xs tracking-wider font-hud mb-1 uppercase">Wins</p>
                <p className="text-2xl font-bold text-omnix-text">∞</p>
              </div>
            </div>

            {/* Match stat */}
            <div className="text-center">
              <p className="text-omnix-blue text-xs tracking-wider font-hud mb-1 uppercase">Match</p>
              <p className="text-xl font-bold text-omnix-text">24</p>
            </div>

            {/* Active provider banner */}
            <div className="flex items-center gap-2 text-omnix-blue/80 text-xs tracking-widest font-hud">
              <RefreshCw className="w-4 h-4 animate-spin-slow" />
              Routing via
              <span className="text-omnix-text">{activeProvider.toUpperCase()}</span>
            </div>
          </div>

          {/* RIGHT COLUMN: Settings */}
          <div className="col-span-4 flex flex-col">
            <Panel className="flex-1 flex flex-col" title="SETTINGS" footer="SETTINGS">
              <div className="flex-1 flex flex-col gap-6">
                {/* Settings Menu */}
                <ul className="space-y-3">
                  {settingsMenu.map(item => {
                    const Icon = item.icon;
                    const isActive = activeSetting === item.id;

                    return (
                      <li
                        key={item.id}
                        className={`group cursor-pointer flex items-center justify-between px-3 py-3 rounded-sm border transition-all ${
                          isActive
                            ? 'border-omnix-blue bg-omnix-blue/10 shadow-[0_0_12px_rgba(0,243,255,0.15)]'
                            : 'border-transparent hover:border-omnix-blue/20 hover:bg-omnix-blue/5'
                        }`}
                        onClick={() => setActiveSetting(item.id)}
                      >
                        <div className="flex items-center gap-3">
                          <Icon className="w-4 h-4 text-omnix-blue" />
                          <span className="text-omnix-text">{item.label}</span>
                        </div>
                        <ChevronRight
                          className={`w-4 h-4 transition-colors ${
                            isActive ? 'text-omnix-blue' : 'text-omnix-blue/50 group-hover:text-omnix-blue'
                          }`}
                        />
                      </li>
                    );
                  })}
                </ul>

                <div className="p-4 border border-omnix-blue/20 rounded-sm bg-omnix-dark/60 space-y-4">
                  {activeSetting === 'overlay' && (
                    <>
                      <div className="flex items-center justify-between gap-2">
                        <div>
                          <p className="text-omnix-text font-semibold">Overlay Layout</p>
                          <p className="text-xs text-omnix-blue/60">Switch between focused HUD or immersive view.</p>
                        </div>
                        <div className="flex gap-2">
                          {(['compact', 'immersive'] as const).map(mode => (
                            <button
                              key={mode}
                              onClick={() => setOverlayMode(mode)}
                              className={`px-3 py-2 text-xs rounded-sm border ${
                                overlayMode === mode
                                  ? 'border-omnix-blue bg-omnix-blue/20 text-omnix-blue'
                                  : 'border-omnix-blue/30 text-omnix-text hover:border-omnix-blue/60'
                              }`}
                            >
                              {mode === 'compact' ? 'Compact' : 'Immersive'}
                            </button>
                          ))}
                        </div>
                      </div>
                      <button
                        onClick={() => setLockPosition(prev => !prev)}
                        className={`w-full flex items-center justify-between px-3 py-2 rounded-sm border text-sm transition-colors ${
                          lockPosition ? 'border-omnix-blue text-omnix-blue bg-omnix-blue/10' : 'border-omnix-blue/30 text-omnix-text hover:border-omnix-blue/50'
                        }`}
                      >
                        <span className="flex items-center gap-2">
                          <Lock className="w-4 h-4" />
                          Lock Overlay Position
                        </span>
                        <span className="uppercase tracking-[0.2em] text-xs">{lockPosition ? 'Locked' : 'Free'}</span>
                      </button>
                    </>
                  )}

                  {activeSetting === 'general' && (
                    <div className="space-y-3">
                      <button
                        onClick={() => toggleSetting('general', 'autoStart')}
                        className={`w-full flex items-center justify-between px-3 py-2 rounded-sm border text-sm ${
                          generalSettings.autoStart ? 'border-omnix-blue text-omnix-blue bg-omnix-blue/10' : 'border-omnix-blue/30 text-omnix-text hover:border-omnix-blue/50'
                        }`}
                      >
                        <span className="flex items-center gap-2"><Power className="w-4 h-4" /> Auto-launch on startup</span>
                        <span className="text-xs tracking-[0.2em] uppercase">{generalSettings.autoStart ? 'On' : 'Off'}</span>
                      </button>
                      <button
                        onClick={() => toggleSetting('general', 'energySaver')}
                        className={`w-full flex items-center justify-between px-3 py-2 rounded-sm border text-sm ${
                          generalSettings.energySaver ? 'border-omnix-blue text-omnix-blue bg-omnix-blue/10' : 'border-omnix-blue/30 text-omnix-text hover:border-omnix-blue/50'
                        }`}
                      >
                        <span className="flex items-center gap-2"><Activity className="w-4 h-4" /> Energy saver mode</span>
                        <span className="text-xs tracking-[0.2em] uppercase">{generalSettings.energySaver ? 'On' : 'Off'}</span>
                      </button>
                      <button
                        onClick={() => toggleSetting('general', 'showTooltips')}
                        className={`w-full flex items-center justify-between px-3 py-2 rounded-sm border text-sm ${
                          generalSettings.showTooltips ? 'border-omnix-blue text-omnix-blue bg-omnix-blue/10' : 'border-omnix-blue/30 text-omnix-text hover:border-omnix-blue/50'
                        }`}
                      >
                        <span className="flex items-center gap-2"><SunMoon className="w-4 h-4" /> HUD tooltips</span>
                        <span className="text-xs tracking-[0.2em] uppercase">{generalSettings.showTooltips ? 'On' : 'Off'}</span>
                      </button>
                    </div>
                  )}

                  {activeSetting === 'notifications' && (
                    <div className="space-y-3">
                      <button
                        onClick={() => toggleSetting('notifications', 'desktop')}
                        className={`w-full flex items-center justify-between px-3 py-2 rounded-sm border text-sm ${
                          notificationSettings.desktop ? 'border-omnix-blue text-omnix-blue bg-omnix-blue/10' : 'border-omnix-blue/30 text-omnix-text hover:border-omnix-blue/50'
                        }`}
                      >
                        <span className="flex items-center gap-2"><MonitorSmartphone className="w-4 h-4" /> Desktop alerts</span>
                        <span className="text-xs tracking-[0.2em] uppercase">{notificationSettings.desktop ? 'On' : 'Off'}</span>
                      </button>
                      <button
                        onClick={() => toggleSetting('notifications', 'sound')}
                        className={`w-full flex items-center justify-between px-3 py-2 rounded-sm border text-sm ${
                          notificationSettings.sound ? 'border-omnix-blue text-omnix-blue bg-omnix-blue/10' : 'border-omnix-blue/30 text-omnix-text hover:border-omnix-blue/50'
                        }`}
                      >
                        <span className="flex items-center gap-2"><Bell className="w-4 h-4" /> Sound cues</span>
                        <span className="text-xs tracking-[0.2em] uppercase">{notificationSettings.sound ? 'On' : 'Mute'}</span>
                      </button>
                      <button
                        onClick={() => toggleSetting('notifications', 'aiUpdates')}
                        className={`w-full flex items-center justify-between px-3 py-2 rounded-sm border text-sm ${
                          notificationSettings.aiUpdates ? 'border-omnix-blue text-omnix-blue bg-omnix-blue/10' : 'border-omnix-blue/30 text-omnix-text hover:border-omnix-blue/50'
                        }`}
                      >
                        <span className="flex items-center gap-2"><RefreshCw className="w-4 h-4" /> AI status pings</span>
                        <span className="text-xs tracking-[0.2em] uppercase">{notificationSettings.aiUpdates ? 'On' : 'Off'}</span>
                      </button>
                    </div>
                  )}

                  {activeSetting === 'privacy' && (
                    <div className="space-y-3">
                      <button
                        onClick={() => toggleSetting('privacy', 'streamerMode')}
                        className={`w-full flex items-center justify-between px-3 py-2 rounded-sm border text-sm ${
                          privacySettings.streamerMode ? 'border-omnix-blue text-omnix-blue bg-omnix-blue/10' : 'border-omnix-blue/30 text-omnix-text hover:border-omnix-blue/50'
                        }`}
                      >
                        <span className="flex items-center gap-2"><ShieldCheck className="w-4 h-4" /> Streamer-safe mode</span>
                        <span className="text-xs tracking-[0.2em] uppercase">{privacySettings.streamerMode ? 'On' : 'Off'}</span>
                      </button>
                      <button
                        onClick={() => toggleSetting('privacy', 'redactLogs')}
                        className={`w-full flex items-center justify-between px-3 py-2 rounded-sm border text-sm ${
                          privacySettings.redactLogs ? 'border-omnix-blue text-omnix-blue bg-omnix-blue/10' : 'border-omnix-blue/30 text-omnix-text hover:border-omnix-blue/50'
                        }`}
                      >
                        <span className="flex items-center gap-2"><Lock className="w-4 h-4" /> Redact sensitive logs</span>
                        <span className="text-xs tracking-[0.2em] uppercase">{privacySettings.redactLogs ? 'On' : 'Off'}</span>
                      </button>
                      <button
                        onClick={() => toggleSetting('privacy', 'shareUsage')}
                        className={`w-full flex items-center justify-between px-3 py-2 rounded-sm border text-sm ${
                          privacySettings.shareUsage ? 'border-omnix-blue text-omnix-blue bg-omnix-blue/10' : 'border-omnix-blue/30 text-omnix-text hover:border-omnix-blue/50'
                        }`}
                      >
                        <span className="flex items-center gap-2"><Circle className="w-4 h-4" /> Share usage metrics</span>
                        <span className="text-xs tracking-[0.2em] uppercase">{privacySettings.shareUsage ? 'On' : 'Off'}</span>
                      </button>
                    </div>
                  )}
                </div>

                {/* AI Provider Section */}
                <div className="mt-6">
                  <div className="flex items-center gap-2 mb-4">
                    <Cpu className="w-4 h-4 text-omnix-blue" />
                    <h4 className="text-omnix-blue font-hud tracking-[0.3em] text-xs uppercase">AI Provider</h4>
                  </div>
                  <div className="space-y-3">
                    <div
                      onClick={() => setActiveProvider('synapse')}
                      className={`cursor-pointer px-4 py-3 border rounded-sm flex items-center gap-4 transition-all ${activeProvider === 'synapse' ? 'border-omnix-blue bg-omnix-blue/5' : 'border-omnix-blue/20 hover:border-omnix-blue/40'}`}
                    >
                      <div className={`w-5 h-5 rounded-full border-2 flex items-center justify-center ${activeProvider === 'synapse' ? 'border-omnix-blue' : 'border-omnix-blue/30'}`}>
                        {activeProvider === 'synapse' && <div className="w-2.5 h-2.5 bg-omnix-blue rounded-full"></div>}
                      </div>
                      <span className="font-hud tracking-widest text-sm text-omnix-text">SYNAPSE</span>
                    </div>

                    <div
                      onClick={() => setActiveProvider('hybridnex')}
                      className={`cursor-pointer px-4 py-3 border rounded-sm flex items-center gap-4 transition-all ${activeProvider === 'hybridnex' ? 'border-omnix-blue bg-omnix-blue/5' : 'border-omnix-blue/20 hover:border-omnix-blue/40'}`}
                    >
                      <div className={`w-5 h-5 rounded-full border-2 flex items-center justify-center ${activeProvider === 'hybridnex' ? 'border-omnix-blue' : 'border-omnix-blue/30'}`}>
                         {activeProvider === 'hybridnex' && <div className="w-2.5 h-2.5 bg-omnix-blue rounded-full"></div>}
                      </div>
                      <span className="font-hud tracking-widest text-sm text-omnix-text">HYBRIDNEX</span>
                    </div>
                  </div>
                </div>
              </div>
            </Panel>
          </div>
        </div>
      </div>
    </div>
    </div>
  );
}
