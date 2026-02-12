# MayBot Admin Interface - Manual Setup Guide

Since npm is not currently available in your system, here's the manual setup process:

## 📥 Prerequisites Installation

### 1. Install Node.js
Download and install Node.js (includes npm) from:
- **Official**: https://nodejs.org/
- **Direct**: https://nodejs.org/dist/v18.19.0/node-v18.19.0-x64.msi

Choose the LTS (Long Term Support) version recommended for Windows.

### 2. Verify Installation
After installation, open a NEW command prompt and run:
```cmd
node --version
npm --version
```

You should see version numbers like:
```
v18.19.0
9.6.7
```

## 🔨 Manual Frontend Build

### 1. Navigate to Frontend Directory
```cmd
cd H:\PYTHON\maybot\frontend
```

### 2. Install Dependencies
```cmd
npm install
```

### 3. Build the Application
```cmd
npm run build
```

### 4. Verify Build
You should see a `dist` folder created inside `frontend` with:
- `index.html`
- `assets/` folder with JS/CSS files

## 🚀 Start the Admin Interface

### Option 1: With Backend Integration
```cmd
cd H:\PYTHON\maybot
uvicorn wa:app --host 192.168.30.50 --port 8998
```

Then access: `http://192.168.30.50:8998/?admin_key=YOUR_ADMIN_PHONE`

### Option 2: Development Mode (for testing)
```cmd
# Terminal 1 - Backend
cd H:\PYTHON\maybot
uvicorn wa:app --host 192.168.30.50 --port 8998

# Terminal 2 - Frontend Dev Server  
cd H:\PYTHON\maybot\frontend
npm run dev
```

Then access: `http://localhost:5173/?admin_key=YOUR_ADMIN_PHONE`

## 🔑 Get Your Admin Key

Find your admin phone number in `config.toml`:
```toml
[CONFIG]
ADMIN_NUMBER = ["62895352277562@c.us", "120363149813038443@g.us"]
```

Use one of these numbers as your admin_key parameter.

## 🎯 Quick Test

1. Start the backend server
2. Open browser to: `http://192.168.30.50:8998/?admin_key=62895352277562@c.us`
3. You should see the admin login page
4. Click "Access Admin Panel" to enter the dashboard

## 📁 Manual Static File Setup (if needed)

If the automatic static serving doesn't work, manually copy files:
```cmd
cd H:\PYTHON\maybot
xcopy frontend\dist\* static\ /E /I
```

## 🔧 Alternative: Use Existing Admin

Remember you can still use the existing Gradio interface:
```cmd
python admin_fe.py
```

This will start the admin interface on port 9666.

## 📞 Troubleshooting

### npm not recognized
1. Restart your computer after Node.js installation
2. Check if npm is in PATH: `where npm`
3. Add to PATH manually if needed

### Build errors
1. Delete `node_modules` and `package-lock.json`
2. Run `npm install` again
3. Check Node.js version compatibility

### Server won't start
1. Check if port 8998 is available: `netstat -ano | findstr 8998`
2. Kill any process using the port: `taskkill /PID <PID> /F`
3. Try a different port: `uvicorn wa:app --port 8999`

### Admin key not working
1. Verify the number is in config.toml ADMIN_NUMBER list
2. Check for typos in the phone number format
3. Ensure it includes "@c.us" or "@g.us" suffix

## 🎉 Success Indicators

✅ **Frontend Built**: You see `dist` folder with assets
✅ **Backend Running**: Server starts without errors
✅ **Login Working**: Admin login page loads
✅ **Dashboard Access**: Main admin interface appears
✅ **Data Loading**: Conversations and statistics display

## 📧 Development Tips

- **Hot Reload**: Use `npm run dev` for auto-refresh on code changes
- **Console**: Check browser DevTools for errors
- **Network**: Monitor API calls in Network tab
- **Backend Logs**: Watch terminal for server errors

The admin interface provides full control over your MayBot system with a modern, responsive design!