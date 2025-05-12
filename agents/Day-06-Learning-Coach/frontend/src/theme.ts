import { createSystem, defaultConfig } from '@chakra-ui/react';

// Create a custom system with our theme configuration
const system = createSystem(defaultConfig, {
  theme: {
    tokens: {
      colors: {
        brand: {
          50: { value: '#e6f7ff' },
          100: { value: '#b3e0ff' },
          200: { value: '#80caff' },
          300: { value: '#4db3ff' },
          400: { value: '#1a9dff' },
          500: { value: '#0080ff' },
          600: { value: '#0066cc' },
          700: { value: '#004d99' },
          800: { value: '#003366' },
          900: { value: '#001a33' },
          950: { value: '#001a33' },
        },
      },
      fonts: {
        heading: { value: 'Inter, system-ui, sans-serif' },
        body: { value: 'Inter, system-ui, sans-serif' },
      },
    },
    semanticTokens: {
      colors: {
        brand: {
          solid: { value: '{colors.brand.500}' },
          contrast: { value: '{colors.brand.100}' },
          fg: { value: '{colors.brand.700}' },
          muted: { value: '{colors.brand.100}' },
          subtle: { value: '{colors.brand.200}' },
          emphasized: { value: '{colors.brand.300}' },
          focusRing: { value: '{colors.brand.500}' },
        },
      },
    },
    recipes: {
      Button: {
        base: {
          fontWeight: 'semibold',
          borderRadius: 'md',
        },
      },
      Card: {
        base: {
          borderRadius: 'lg',
          overflow: 'hidden',
          boxShadow: 'md',
        },
      },
    },
  },
});

export default system;
