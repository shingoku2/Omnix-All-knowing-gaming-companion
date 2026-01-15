import { describe, it, expect } from 'vitest';
import resolveConfig from 'tailwindcss/resolveConfig';
import tailwindConfig from '../tailwind.config.js';

const config = resolveConfig(tailwindConfig);

describe('Tailwind Design Tokens', () => {
  it('should have the "cyberpunk" color palette defined', () => {
    const colors = config.theme?.colors as any;
    
    expect(colors.omnix).toBeDefined();
    expect(colors.omnix.bg).toBeDefined();
    expect(colors.omnix.bg.dark).toBe('#030610'); // Deepest space/void color
    expect(colors.omnix.bg.panel).toBe('rgba(8, 14, 28, 0.90)'); // High opacity panel
    
    expect(colors.omnix.primary).toBe('#00f0ff'); // Cyberpunk Cyan
    expect(colors.omnix.primaryDim).toBe('rgba(0, 240, 255, 0.15)');
    
    expect(colors.omnix.secondary).toBe('#ff0099'); // Cyberpunk Magenta/Pink
    expect(colors.omnix.secondaryDim).toBe('rgba(255, 0, 153, 0.15)');

    expect(colors.omnix.accent).toBe('#fcee0a'); // Cyberpunk Yellow/Gold
    
    expect(colors.omnix.text).toBeDefined();
    expect(colors.omnix.text.primary).toBe('#e0f7ff');
    expect(colors.omnix.text.secondary).toBe('#94a3b8');
  });

  it('should have custom box shadows for neon glows', () => {
    const boxShadow = config.theme?.boxShadow as any;
    expect(boxShadow['neon-cyan']).toBeDefined();
    expect(boxShadow['neon-magenta']).toBeDefined();
  });
});
