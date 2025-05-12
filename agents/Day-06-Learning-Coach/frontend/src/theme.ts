import { createSystem, defaultConfig } from '@chakra-ui/react';

// Create a custom system with our theme configuration
const system = createSystem(defaultConfig, {
  theme: {
    tokens: {
      colors: {
        // Primary brand color - blue
        brand: {
          50: { value: '#e6f7ff' },
          100: { value: '#b3e0ff' },
          200: { value: '#80caff' },
          300: { value: '#4db3ff' },
          400: { value: '#1a9dff' },
          500: { value: '#0080ff' }, // Primary brand color
          600: { value: '#0066cc' }, // Used for navbar/footer
          700: { value: '#004d99' },
          800: { value: '#003366' },
          900: { value: '#001a33' },
          950: { value: '#001a33' },
        },
        // Resource type colors
        resource: {
          article: { value: '#3182ce' }, // blue
          video: { value: '#e53e3e' },   // red
          course: { value: '#38a169' },  // green
          book: { value: '#805ad5' },    // purple
          tutorial: { value: '#dd6b20' }, // orange
        },
        // Quiz difficulty colors
        difficulty: {
          beginner: { value: '#38a169' },    // green
          intermediate: { value: '#3182ce' }, // blue
          advanced: { value: '#805ad5' },    // purple
          expert: { value: '#e53e3e' },      // red
        },
      },
      fonts: {
        heading: { value: 'Inter, system-ui, sans-serif' },
        body: { value: 'Inter, system-ui, sans-serif' },
      },
    },
    semanticTokens: {
      colors: {
        // Brand semantic tokens
        brand: {
          solid: { value: '{colors.brand.500}' },
          contrast: { value: '{colors.brand.100}' },
          fg: { value: '{colors.brand.700}' },
          muted: { value: '{colors.brand.100}' },
          subtle: { value: '{colors.brand.200}' },
          emphasized: { value: '{colors.brand.300}' },
          focusRing: { value: '{colors.brand.500}' },
        },
        // App-specific semantic tokens
        app: {
          // Navbar and footer
          navbar: { value: '{colors.brand.600}' },
          footer: { value: '{colors.brand.600}' },
          navbarText: { value: 'white' },
          footerText: { value: 'white' },

          // Chat interface
          userBubble: {
            value: { _light: '{colors.brand.100}', _dark: '{colors.brand.600}' }
          },
          agentBubble: {
            value: { _light: '{colors.gray.200}', _dark: '{colors.gray.700}' }
          },

          // Background and Cards
          pageBg: {
            value: { _light: '{colors.gray.50}', _dark: '{colors.gray.800}' }
          },
          cardBg: {
            value: { _light: 'white', _dark: '{colors.gray.700}' }
          },
          cardBorder: {
            value: { _light: '{colors.gray.200}', _dark: '{colors.gray.600}' }
          },

          // Text
          pageTitleColor: {
            value: { _light: '{colors.brand.800}', _dark: '{colors.brand.200}' }
          },
          headingColor: {
            value: { _light: '{colors.brand.700}', _dark: '{colors.brand.200}' }
          },
          textColor: {
            value: { _light: '{colors.gray.800}', _dark: 'white' }
          },
          mutedText: {
            value: { _light: '{colors.gray.500}', _dark: '{colors.gray.400}' }
          },
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
