# Local Testing Guide - OVPFH v2.0

## Quick Start

This is a **static website** (HTML/CSS/JavaScript) - no build process or npm required!

### Method 1: Python HTTP Server (Recommended)

Since you have Python installed (`.venv` folder exists), use Python's built-in HTTP server:

```powershell
# Activate your virtual environment (optional, but good practice)
& .venv/Scripts/Activate.ps1

# Start HTTP server on port 8000
python -m http.server 8000
```

Then open in your browser:
```
http://localhost:8000
```

**Why this method?**
- Handles CORS properly for ES modules (Firebase imports)
- Serves files with correct MIME types
- Simple and reliable

### Method 2: VS Code Live Server

If you have VS Code with Live Server extension:

1. Right-click on `index.html`
2. Select "Open with Live Server"
3. Browser opens automatically

### Method 3: Direct File Opening (Limited)

⚠️ **Not recommended** - Firebase modules won't work due to CORS restrictions

```powershell
# Open directly in browser
start index.html
```

## Testing Checklist

### 1. Basic Functionality
- [ ] Page loads without errors
- [ ] Match cards display
- [ ] Filters work (team, tournament, date)
- [ ] Search works
- [ ] Keyboard shortcuts work (press `?` for help)

### 2. Authentication
- [ ] Click "🔐 Entrar" button
- [ ] Auth modal opens
- [ ] Can switch between Login/Signup tabs
- [ ] Form validation works
- [ ] Can create account
- [ ] Can login
- [ ] Google sign-in works
- [ ] User menu appears after login
- [ ] Can logout

### 3. Design & Animations
- [ ] Bebas Neue font loads
- [ ] Cyan/orange colors display correctly
- [ ] Match cards animate on load
- [ ] Hover effects work
- [ ] Loading skeletons appear
- [ ] Toast notifications work

### 4. Keyboard Shortcuts
- [ ] `/` - Focus search
- [ ] `←/→` - Navigate dates
- [ ] `Esc` - Clear search / Close modal
- [ ] `?` - Show keyboard help

### 5. Responsive Design
- [ ] Resize browser window
- [ ] Check mobile view (320px)
- [ ] Check tablet view (768px)
- [ ] Check desktop view (1024px+)

## Browser Console Checks

Open Developer Tools (F12) and check:

### Expected Console Messages
```
🔥 Firebase initialized successfully
📊 Analytics enabled
⚽ Onde Vai Passar Futebol Hoje v2.0 - Initialized
📅 Loaded X matches
✨ Nielsen Heuristics: H1 (Status), H3 (Control), H7 (Efficiency)
```

### Common Errors & Solutions

**Error: "Failed to load module script"**
- **Cause**: Opening file directly (file://)
- **Solution**: Use HTTP server (Method 1 or 2)

**Error: "CORS policy"**
- **Cause**: ES modules require HTTP server
- **Solution**: Use Python HTTP server

**Error: "Firebase not defined"**
- **Cause**: Scripts not loading
- **Solution**: Check browser console, ensure HTTP server is running

**Error: "No matches found"**
- **Cause**: JSON files not loading
- **Solution**: Check `data/` folder exists with JSON files

## Testing Firebase Authentication

### 1. Create Test Account

```
Email: test@example.com
Password: test123
Name: Test User
```

### 2. Test Google Sign-In

- Click "Continuar com Google"
- Select your Google account
- Verify login success

### 3. Test Logout

- Click user avatar/name
- Click "Sair"
- Verify logout success

## Performance Testing

### Check Loading Speed

1. Open DevTools → Network tab
2. Reload page (Ctrl+Shift+R)
3. Check:
   - Total load time < 2 seconds
   - Firebase scripts load successfully
   - CSS/JS files load

### Check Animations

1. Open DevTools → Performance tab
2. Record page load
3. Check FPS stays at 60fps

## Troubleshooting

### Firebase Authentication Not Working

**Check Firebase Console:**
1. Go to https://console.firebase.google.com/
2. Select project: `ovpfh-28cee`
3. Go to Authentication → Settings
4. Add authorized domain: `localhost`

### Styles Not Loading

**Check file paths:**
```powershell
# Verify CSS files exist
ls css/

# Should show:
# design-tokens.css
# animations.css
# components.css
# auth-modal.css
```

### JavaScript Errors

**Check script order in index.html:**
```html
<!-- Regular scripts first -->
<script src="router.js"></script>
<script src="app.js"></script>
<script src="js/keyboard-shortcuts.js"></script>

<!-- ES Modules last -->
<script type="module" src="js/firebase-config.js"></script>
<script type="module" src="js/auth.js"></script>
<script type="module" src="js/auth-modal.js"></script>
<script type="module" src="js/auth-state.js"></script>
```

## Production Deployment

When ready to deploy:

### Option 1: Static Hosting (Recommended)

**Firebase Hosting:**
```powershell
# Install Firebase CLI
npm install -g firebase-tools

# Login
firebase login

# Initialize
firebase init hosting

# Deploy
firebase deploy
```

**Netlify:**
1. Drag and drop project folder to netlify.com
2. Done!

**Vercel:**
```powershell
npm install -g vercel
vercel
```

### Option 2: Your VPS (Hostinger)

Upload files via FTP/SFTP to your web server root directory.

## Quick Commands Reference

```powershell
# Start local server
python -m http.server 8000

# Open in browser
start http://localhost:8000

# Check Python version
python --version

# Activate virtual environment
& .venv/Scripts/Activate.ps1

# Deactivate virtual environment
deactivate
```

## Need Help?

### Check These Files
- `md/FIREBASE_AUTH.md` - Firebase authentication guide
- `C:\Users\Neto\.gemini\antigravity\brain\...\walkthrough.md` - v2.0 features walkthrough
- Browser DevTools Console - Error messages

### Common Questions

**Q: Do I need Node.js/npm?**
A: No! This is a static site. Only need Python HTTP server.

**Q: Why use HTTP server instead of opening file directly?**
A: Firebase ES modules require HTTP protocol, not file:// protocol.

**Q: Can I use a different port?**
A: Yes! `python -m http.server 3000` (or any port)

**Q: How do I stop the server?**
A: Press `Ctrl+C` in the terminal

---

**Happy Testing! 🚀**
