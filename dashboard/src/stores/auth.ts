import { create } from 'zustand';
import {
  onAuthStateChanged,
  signInWithEmailAndPassword,
  createUserWithEmailAndPassword,
  signInWithPopup,
  GoogleAuthProvider,
  signOut as firebaseSignOut,
  type User,
} from 'firebase/auth';
import { auth } from '../lib/firebase';

interface AuthState {
  user: User | null;
  loading: boolean;
  signIn: (email: string, password: string) => Promise<void>;
  signUp: (email: string, password: string) => Promise<void>;
  signInWithGoogle: () => Promise<void>;
  signOut: () => Promise<void>;
}

export const useAuthStore = create<AuthState>((set) => {
  // Listen for auth state changes
  onAuthStateChanged(auth, (user) => {
    set({ user, loading: false });
  });

  return {
    user: null,
    loading: true,

    signIn: async (email, password) => {
      await signInWithEmailAndPassword(auth, email, password);
    },

    signUp: async (email, password) => {
      await createUserWithEmailAndPassword(auth, email, password);
    },

    signInWithGoogle: async () => {
      await signInWithPopup(auth, new GoogleAuthProvider());
    },

    signOut: async () => {
      await firebaseSignOut(auth);
    },
  };
});
