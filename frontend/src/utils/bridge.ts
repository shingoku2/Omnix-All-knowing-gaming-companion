import { QWebChannel } from 'qwebchannel';

/* eslint-disable @typescript-eslint/no-explicit-any */
declare global {
  interface Window {
    qt: any;
    bridge: any;
  }
}

class Bridge {
  private bridge: any = null;

  constructor() {
    this.init();
  }

  private init() {
    if (window.qt && window.qt.webChannelTransport) {
      new QWebChannel(window.qt.webChannelTransport, (channel: any) => {
        this.bridge = channel.objects.bridge;
        // console.debug('Bridge initialized');
        
        // Connect signals
        this.bridge.messageReceived.connect((content: string) => {
          this.onMessageReceived(content);
        });
      });
    } else {
      console.warn('Qt WebChannel transport not found. Running in browser mode?');
    }
  }

  private onMessageReceived: (content: string) => void = () => {};

  public setMessageListener(callback: (content: string) => void) {
    this.onMessageReceived = callback;
  }

  public sendMessage(content: string) {
    if (this.bridge) {
      this.bridge.sendMessage(content);
    } else {
      console.debug('[Mock] sendMessage:', content);
    }
  }

  public toggleOverlay() {
    if (this.bridge) {
      this.bridge.toggleOverlay();
    } else {
      console.debug('[Mock] toggleOverlay');
    }
  }
}

export const bridge = new Bridge();
