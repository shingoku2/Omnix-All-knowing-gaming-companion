import { render, screen, fireEvent } from '@testing-library/react';
import { ChatModule } from './ChatModule';
import { describe, it, expect, vi } from 'vitest';

describe('ChatModule', () => {
  const messages = [
    { id: '1', role: 'assistant', content: 'Hello! How can I help you today?' },
    { id: '2', role: 'user', content: 'Tell me about the game mechanics.' },
  ];

  it('renders existing messages', () => {
    render(<ChatModule messages={messages} onSendMessage={() => {}} />);
    expect(screen.getByText('Hello! How can I help you today?')).toBeInTheDocument();
    expect(screen.getByText('Tell me about the game mechanics.')).toBeInTheDocument();
  });

  it('calls onSendMessage when the form is submitted', () => {
    const onSendMessage = vi.fn();
    render(<ChatModule messages={[]} onSendMessage={onSendMessage} />);
    
    const input = screen.getByPlaceholderText(/Type your message/i);
    fireEvent.change(input, { target: { value: 'New message' } });
    
    // Find the send button or submit the form
    const form = input.closest('form');
    if (form) {
      fireEvent.submit(form);
    }
    
    expect(onSendMessage).toHaveBeenCalledWith('New message');
  });

  it('has the correct cyberpunk styling classes', () => {
    render(<ChatModule messages={[]} onSendMessage={() => {}} />);
    const container = screen.getByTestId('chat-module');
    expect(container).toHaveClass('omni-frame');
  });
});
