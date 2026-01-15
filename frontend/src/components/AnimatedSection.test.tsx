import { render, screen } from '@testing-library/react';
import { AnimatedSection } from './AnimatedSection';
import { describe, it, expect } from 'vitest';

describe('AnimatedSection', () => {
  it('renders children correctly', () => {
    render(
      <AnimatedSection>
        <div data-testid="child">Content</div>
      </AnimatedSection>
    );
    expect(screen.getByTestId('child')).toBeInTheDocument();
  });
});
