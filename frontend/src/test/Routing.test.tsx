import { render, screen, fireEvent } from '@testing-library/react';
import App from '../App';
import { describe, it, expect } from 'vitest';

describe('App Navigation Routing', () => {
  it('switches between chat and settings when clicking menu items', () => {
    render(<App />);
    
    // Default should be chat
    expect(screen.getByText(/Neural Assistant/i)).toBeInTheDocument();
    
    // Click Settings in RightSideMenu (using label from MenuItem)
    const settingsButton = screen.getByTitle('Settings');
    fireEvent.click(settingsButton);
    
    // Now Settings should be visible
    expect(screen.getByText(/System Configuration/i)).toBeInTheDocument();
    expect(screen.queryByText(/Neural Assistant/i)).not.toBeInTheDocument();
  });
});
