import { render, screen } from '@testing-library/react';
import { MainContainer } from './MainContainer';
import { describe, it, expect } from 'vitest';

describe('MainContainer', () => {
  it('renders with the .omni-frame class', () => {
    render(<MainContainer>Test Content</MainContainer>);
    const container = screen.getByTestId('main-container');
    expect(container).toHaveClass('omni-frame');
  });

  it('contains the children passed to it', () => {
    render(<MainContainer>Test Content</MainContainer>);
    expect(screen.getByText('Test Content')).toBeInTheDocument();
  });
});
