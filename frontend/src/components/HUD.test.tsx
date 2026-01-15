import { render, screen } from '@testing-library/react';
import { CentralHUD } from './CentralHUD';
import { Footer } from './Footer';
import { describe, it, expect } from 'vitest';

describe('CentralHUD', () => {
  it('renders the game status indicator', () => {
    render(<CentralHUD gameName="Cyberpunk 2077" isDetected={true} />);
    expect(screen.getByText('Cyberpunk 2077')).toBeInTheDocument();
    expect(screen.getByText(/SYSTEM ACTIVE/i)).toBeInTheDocument();
  });

  it('shows searching status when no game is detected', () => {
    render(<CentralHUD gameName="" isDetected={false} />);
    expect(screen.getByText(/SEARCHING FOR TARGET/i)).toBeInTheDocument();
  });
});

describe('Footer', () => {
  it('renders system metrics', () => {
    render(<Footer cpu="1.2%" ram="256MB" version="v2.1.0" />);
    expect(screen.getByText('1.2%')).toBeInTheDocument();
    expect(screen.getByText('256MB')).toBeInTheDocument();
    expect(screen.getByText(/v2.1.0/)).toBeInTheDocument();
  });
});
