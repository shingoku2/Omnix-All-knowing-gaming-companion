import { describe, it, expect } from 'vitest';
import fs from 'fs';
import path from 'path';

describe('Global CSS Utilities', () => {
  it('should define the .omni-frame component class', () => {
    const cssPath = path.resolve(__dirname, 'index.css');
    const cssContent = fs.readFileSync(cssPath, 'utf-8');
    
    expect(cssContent).toContain('.omni-frame');
  });

  it('should define the .omni-glow utility', () => {
    const cssPath = path.resolve(__dirname, 'index.css');
    const cssContent = fs.readFileSync(cssPath, 'utf-8');
    
    expect(cssContent).toContain('.omni-glow');
  });
  
  it('should define the .omni-text-glow utility', () => {
    const cssPath = path.resolve(__dirname, 'index.css');
    const cssContent = fs.readFileSync(cssPath, 'utf-8');
    
    expect(cssContent).toContain('.omni-text-glow');
  });
});
