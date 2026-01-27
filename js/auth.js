/**
 * OVPFH v2.0 - Authentication Service
 * Handles all Firebase authentication operations
 */

import { auth } from './firebase-config.js';
import {
    createUserWithEmailAndPassword,
    signInWithEmailAndPassword,
    signOut as firebaseSignOut,
    onAuthStateChanged,
    GoogleAuthProvider,
    signInWithPopup,
    updateProfile,
    sendPasswordResetEmail,
    sendEmailVerification
} from 'https://www.gstatic.com/firebasejs/10.7.1/firebase-auth.js';

// Google OAuth provider
const googleProvider = new GoogleAuthProvider();

/**
 * Error messages in Portuguese
 */
const errorMessages = {
    'auth/email-already-in-use': 'Este e-mail já está em uso',
    'auth/invalid-email': 'E-mail inválido',
    'auth/user-not-found': 'Usuário não encontrado',
    'auth/wrong-password': 'Senha incorreta',
    'auth/weak-password': 'A senha deve ter no mínimo 6 caracteres',
    'auth/network-request-failed': 'Erro de conexão. Verifique sua internet.',
    'auth/too-many-requests': 'Muitas tentativas. Aguarde um momento.',
    'auth/operation-not-allowed': 'Operação não permitida',
    'auth/popup-closed-by-user': 'Login cancelado',
    'auth/cancelled-popup-request': 'Login cancelado',
    'auth/popup-blocked': 'Popup bloqueado. Permita popups para este site.',
    'auth/email-not-verified': 'Por favor, verifique seu e-mail antes de fazer login.',
    'default': 'Ocorreu um erro. Tente novamente.'
};

/**
 * Get user-friendly error message
 */
function getErrorMessage(error) {
    return errorMessages[error.code] || errorMessages.default;
}

/**
 * Sign up with email and password
 * @param {string} email - User email
 * @param {string} password - User password
 * @param {string} displayName - User display name (optional)
 * @returns {Promise<Object>} Result object with success status
 */
export async function signUp(email, password, displayName = null) {
    try {
        const userCredential = await createUserWithEmailAndPassword(auth, email, password);

        // Update display name if provided
        if (displayName) {
            await updateProfile(userCredential.user, { displayName });
        }

        // Send email verification
        await sendEmailVerification(userCredential.user);

        // Sign out immediately - user must verify email first
        await firebaseSignOut(auth);

        console.log('✅ User signed up, verification email sent:', userCredential.user.email);
        return {
            success: true,
            email: userCredential.user.email,
            needsVerification: true
        };
    } catch (error) {
        console.error('❌ Signup error:', error);
        return {
            success: false,
            error: getErrorMessage(error)
        };
    }
}

/**
 * Sign in with email and password
 * @param {string} email - User email
 * @param {string} password - User password
 * @returns {Promise<Object>} Result object
 */
export async function signIn(email, password) {
    try {
        const userCredential = await signInWithEmailAndPassword(auth, email, password);

        // Check if email is verified
        if (!userCredential.user.emailVerified) {
            // Sign out immediately
            await firebaseSignOut(auth);

            console.log('❌ Email not verified:', userCredential.user.email);
            return {
                success: false,
                needsVerification: true,
                email: userCredential.user.email,
                error: 'Por favor, verifique seu e-mail antes de fazer login.'
            };
        }

        console.log('✅ User signed in:', userCredential.user.email);
        return {
            success: true,
            user: userCredential.user
        };
    } catch (error) {
        console.error('❌ Signin error:', error);
        return {
            success: false,
            error: getErrorMessage(error)
        };
    }
}

/**
 * Sign in with Google
 * @returns {Promise<Object>} User object
 */
export async function signInWithGoogle() {
    try {
        const result = await signInWithPopup(auth, googleProvider);
        console.log('✅ User signed in with Google:', result.user.email);
        return {
            success: true,
            user: result.user
        };
    } catch (error) {
        console.error('❌ Google signin error:', error);
        return {
            success: false,
            error: getErrorMessage(error)
        };
    }
}

/**
 * Sign out current user
 * @returns {Promise<Object>} Success status
 */
export async function signOut() {
    try {
        await firebaseSignOut(auth);
        console.log('✅ User signed out');
        return {
            success: true
        };
    } catch (error) {
        console.error('❌ Signout error:', error);
        return {
            success: false,
            error: getErrorMessage(error)
        };
    }
}

/**
 * Send password reset email
 * @param {string} email - User email
 * @returns {Promise<Object>} Success status
 */
export async function resetPassword(email) {
    try {
        await sendPasswordResetEmail(auth, email);
        console.log('✅ Password reset email sent to:', email);
        return {
            success: true,
            message: 'E-mail de recuperação enviado. Verifique sua caixa de entrada.'
        };
    } catch (error) {
        console.error('❌ Password reset error:', error);
        return {
            success: false,
            error: getErrorMessage(error)
        };
    }
}

/**
 * Resend verification email to current user
 * @returns {Promise<Object>} Success status
 */
export async function resendVerificationEmail() {
    try {
        const user = auth.currentUser;
        if (!user) {
            return {
                success: false,
                error: 'Nenhum usuário conectado'
            };
        }

        if (user.emailVerified) {
            return {
                success: false,
                error: 'E-mail já verificado'
            };
        }

        await sendEmailVerification(user);
        console.log('✅ Verification email resent to:', user.email);
        return {
            success: true,
            message: 'E-mail de verificação reenviado'
        };
    } catch (error) {
        console.error('❌ Resend verification error:', error);
        return {
            success: false,
            error: getErrorMessage(error)
        };
    }
}

/**
 * Check if current user's email is verified
 * @returns {boolean} True if email is verified
 */
export function isEmailVerified() {
    const user = auth.currentUser;
    return user ? user.emailVerified : false;
}

/**
 * Get current user
 * @returns {Object|null} Current user or null
 */
export function getCurrentUser() {
    return auth.currentUser;
}

/**
 * Listen to authentication state changes
 * @param {Function} callback - Callback function with user parameter
 * @returns {Function} Unsubscribe function
 */
export function onAuthStateChange(callback) {
    return onAuthStateChanged(auth, (user) => {
        callback(user);
    });
}

/**
 * Check if user is authenticated
 * @returns {boolean} True if user is logged in
 */
export function isAuthenticated() {
    return auth.currentUser !== null;
}

/**
 * Get user display name or email
 * @returns {string} User display name or email
 */
export function getUserDisplayName() {
    const user = auth.currentUser;
    if (!user) return '';
    return user.displayName || user.email.split('@')[0];
}

/**
 * Get user email
 * @returns {string} User email
 */
export function getUserEmail() {
    const user = auth.currentUser;
    return user ? user.email : '';
}

/**
 * Get user photo URL
 * @returns {string|null} User photo URL or null
 */
export function getUserPhotoURL() {
    const user = auth.currentUser;
    return user ? user.photoURL : null;
}
