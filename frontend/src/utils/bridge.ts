import { QWebChannel } from 'qwebchannel';

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
        console.log('Bridge initialized');
        
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
      console.log('[Mock] sendMessage:', content);
    }
  }

  public toggleOverlay() {
    if (this.bridge) {
      this.bridge.toggleOverlay();
    } else {
      console.log('[Mock] toggleOverlay');
    }
  }
}

export const bridge = new Bridge();
