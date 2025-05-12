"use client";

import { createContext, useContext, useEffect, useState } from "react";
import { IconButton, Skeleton } from "@chakra-ui/react";
import { ClientOnly } from "@chakra-ui/react";

// Create a context for color mode
type ColorMode = "light" | "dark";
type ColorModeContextType = {
  colorMode: ColorMode;
  setColorMode: (mode: ColorMode) => void;
  toggleColorMode: () => void;
};

const ColorModeContext = createContext<ColorModeContextType>({
  colorMode: "light",
  setColorMode: () => {},
  toggleColorMode: () => {},
});

// Provider component
export const ColorModeProvider = ({ children }: { children: React.ReactNode }) => {
  const [colorMode, setColorMode] = useState<ColorMode>("light");

  useEffect(() => {
    // Check if user has a preference in localStorage
    const savedColorMode = localStorage.getItem("chakra-ui-color-mode") as ColorMode | null;
    
    // Check if user has a system preference
    const systemPreference = window.matchMedia("(prefers-color-scheme: dark)").matches
      ? "dark"
      : "light";
    
    // Use saved preference or system preference
    const initialColorMode = savedColorMode || systemPreference;
    setColorMode(initialColorMode);
    document.documentElement.dataset.theme = initialColorMode;
  }, []);

  const setColorModeValue = (mode: ColorMode) => {
    setColorMode(mode);
    localStorage.setItem("chakra-ui-color-mode", mode);
    document.documentElement.dataset.theme = mode;
  };

  const toggleColorMode = () => {
    setColorModeValue(colorMode === "light" ? "dark" : "light");
  };

  return (
    <ColorModeContext.Provider
      value={{ colorMode, setColorMode: setColorModeValue, toggleColorMode }}
    >
      {children}
    </ColorModeContext.Provider>
  );
};

// Hook to use color mode
export const useColorMode = () => {
  const context = useContext(ColorModeContext);
  if (context === undefined) {
    throw new Error("useColorMode must be used within a ColorModeProvider");
  }
  return context;
};

// Hook to use color mode value
export const useColorModeValue = <T,>(lightValue: T, darkValue: T): T => {
  const { colorMode } = useColorMode();
  return colorMode === "light" ? lightValue : darkValue;
};

// Components for forced color mode
export const LightMode = ({ children }: { children: React.ReactNode }) => {
  return <div data-theme="light">{children}</div>;
};

export const DarkMode = ({ children }: { children: React.ReactNode }) => {
  return <div data-theme="dark">{children}</div>;
};

// Color mode button component
export const ColorModeButton = () => {
  const { toggleColorMode, colorMode } = useColorMode();
  
  return (
    <ClientOnly fallback={<Skeleton boxSize="8" />}>
      <IconButton
        aria-label="Toggle color mode"
        icon={colorMode === "light" ? <span>🌙</span> : <span>☀️</span>}
        onClick={toggleColorMode}
        variant="ghost"
      />
    </ClientOnly>
  );
};
