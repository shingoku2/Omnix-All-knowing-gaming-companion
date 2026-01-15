import { render, screen, fireEvent } from '@testing-library/react';
import { RightSideMenu } from './RightSideMenu';
import { describe, it, expect, vi } from 'vitest';

describe('RightSideMenu', () => {
  const items = [
    { id: 'chat', label: 'AI Chat', icon: 'MessageSquare' },
    { id: 'settings', label: 'Settings', icon: 'Settings' },
  ];

  it('renders all navigation items', () => {
    render(<RightSideMenu items={items} activeId="chat" onSelect={() => {}} />);
    expect(screen.getByText('AI Chat')).toBeInTheDocument();
    expect(screen.getByText('Settings')).toBeInTheDocument();
  });

  it('highlights the active item', () => {
    render(<RightSideMenu items={items} activeId="chat" onSelect={() => {}} />);
    const activeItem = screen.getByText('AI Chat').closest('button');
    expect(activeItem).toHaveClass('text-omnix-primary');
  });

  it('calls onSelect when an item is clicked', () => {
    const onSelect = vi.fn();
    render(<RightSideMenu items={items} activeId="chat" onSelect={onSelect} />);
    
    fireEvent.click(screen.getByText('Settings'));
    expect(onSelect).toHaveBeenCalledWith('settings');
  });
});
