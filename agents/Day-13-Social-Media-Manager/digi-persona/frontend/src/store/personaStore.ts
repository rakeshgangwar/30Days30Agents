import { create } from "zustand";
import { Persona } from "@/api/personaService";
import personaService from "@/api/personaService";

interface PersonaState {
  personas: Persona[];
  activePersona: Persona | null;
  isLoading: boolean;
  error: string | null;
  fetchPersonas: () => Promise<void>;
  setActivePersona: (personaId: number) => Promise<void>;
  createPersona: (persona: any) => Promise<Persona>;
  updatePersona: (id: number, persona: any) => Promise<Persona>;
  deletePersona: (id: number) => Promise<void>;
}

export const usePersonaStore = create<PersonaState>((set, get) => ({
  personas: [],
  activePersona: null,
  isLoading: false,
  error: null,

  fetchPersonas: async () => {
    set({ isLoading: true, error: null });
    try {
      const response = await personaService.getPersonas();
      set({ personas: response.items, isLoading: false });

      // Set active persona if not already set
      const activePersonaId = personaService.getActivePersonaId();
      if (activePersonaId && !get().activePersona) {
        const activePersona = response.items.find(p => p.id === activePersonaId);
        if (activePersona) {
          set({ activePersona });
        } else if (response.items.length > 0) {
          // If active persona not found, set first persona as active
          set({ activePersona: response.items[0] });
          personaService.setActivePersona(response.items[0].id);
        }
      } else if (!activePersonaId && response.items.length > 0) {
        // If no active persona set and personas exist, set first persona as active
        set({ activePersona: response.items[0] });
        personaService.setActivePersona(response.items[0].id);
      }
    } catch (error) {
      set({ error: "Failed to fetch personas", isLoading: false });
      console.error("Error fetching personas:", error);
    }
  },

  setActivePersona: async (personaId: number) => {
    set({ isLoading: true, error: null });
    try {
      const persona = get().personas.find(p => p.id === personaId);
      if (persona) {
        set({ activePersona: persona, isLoading: false });
        personaService.setActivePersona(personaId);
      } else {
        const fetchedPersona = await personaService.getPersona(personaId);
        set({ activePersona: fetchedPersona, isLoading: false });
        personaService.setActivePersona(personaId);
      }
    } catch (error) {
      set({ error: "Failed to set active persona", isLoading: false });
      console.error("Error setting active persona:", error);
    }
  },

  createPersona: async (persona: any) => {
    set({ isLoading: true, error: null });
    try {
      const newPersona = await personaService.createPersona(persona);
      set(state => ({ 
        personas: [...state.personas, newPersona], 
        isLoading: false 
      }));
      return newPersona;
    } catch (error) {
      set({ error: "Failed to create persona", isLoading: false });
      console.error("Error creating persona:", error);
      throw error;
    }
  },

  updatePersona: async (id: number, persona: any) => {
    set({ isLoading: true, error: null });
    try {
      const updatedPersona = await personaService.updatePersona(id, persona);
      set(state => ({
        personas: state.personas.map(p => p.id === id ? updatedPersona : p),
        activePersona: state.activePersona?.id === id ? updatedPersona : state.activePersona,
        isLoading: false
      }));
      return updatedPersona;
    } catch (error) {
      set({ error: "Failed to update persona", isLoading: false });
      console.error("Error updating persona:", error);
      throw error;
    }
  },

  deletePersona: async (id: number) => {
    set({ isLoading: true, error: null });
    try {
      await personaService.deletePersona(id);
      set(state => {
        const newPersonas = state.personas.filter(p => p.id !== id);
        let newActivePersona = state.activePersona;
        
        // If deleted persona was active, set a new active persona
        if (state.activePersona?.id === id) {
          newActivePersona = newPersonas.length > 0 ? newPersonas[0] : null;
          if (newActivePersona) {
            personaService.setActivePersona(newActivePersona.id);
          } else {
            localStorage.removeItem("active_persona_id");
          }
        }
        
        return {
          personas: newPersonas,
          activePersona: newActivePersona,
          isLoading: false
        };
      });
    } catch (error) {
      set({ error: "Failed to delete persona", isLoading: false });
      console.error("Error deleting persona:", error);
      throw error;
    }
  }
}));
