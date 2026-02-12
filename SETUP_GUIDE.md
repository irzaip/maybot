# MayBot Admin Interface - Final Instructions

## 🚀 Quick Start

Since npm is not in your system PATH, here are the step-by-step instructions:

### Step 1: Install Node.js (if not already installed)

1. **Download Node.js**: Go to https://nodejs.org/ and download the LTS version
2. **Install**: Run the installer with default settings  
3. **Verify**: Open a NEW command prompt and run:
   ```cmd
   node --version
   npm --version
   ```
   You should see version numbers like `v18.19.0` and `9.6.7`

### Step 2: Build Frontend Manually

1. **Open Command Prompt** (Windows) or Terminal (Mac/Linux)
2. **Navigate to maybot directory**:
   ```cmd
   cd H:\PYTHON\maybot
   ```
3. **Navigate to frontend directory**:
   ```cmd
   cd frontend
   ```
4. **Install dependencies**:
   ```cmd
   npm install
   ```
   This will take 2-5 minutes the first time
5. **Build the project**:
   ```cmd
   npm run build
   ```
   This creates a `dist` folder with the built frontend
6. **Go back to maybot directory**:
   ```cmd
   cd ..
   ```

### Step 3: Copy Built Files

The build should automatically create a `static` folder, but if needed:

1. **Check if static directory exists**:
   ```cmd
   dir static
   ```
2. **If not, create it manually**:
   ```cmd
   mkdir static
   xcopy frontend\dist\* static\ /E /I /Y
   ```

### Step 4: Start Server

```cmd
uvicorn wa:app --host 192.168.30.50 --port 8998
```

### Step 5: Access Admin Interface

Open your web browser and go to:
```
http://192.168.30.50:8998/?admin_key=YOUR_ADMIN_PHONE
```

**Get your admin key** from `config.toml`:
- Open `config.toml` file
- Look for `ADMIN_NUMBER` list
- Use one of the phone numbers (e.g., `62895352277562@c.us`)

## 🎯 What You Get

### Admin Dashboard Features:
- **System Status**: Server status, conversation counts, maintenance mode
- **Conversation Management**: List, search, filter all conversations
- **Persona Control**: Switch between 13 AI personas (ASSISTANT, HRD, SALES_CS, etc.)
- **Mode Settings**: Configure conversation modes (CHITCHAT, ASK, INTERVIEW, etc.)
- **Usage Management**: Control free tries, paid messages, GPT access
- **Direct Messaging**: Send messages directly to users
- **Bulk Operations**: Apply settings to multiple conversations at once
- **Real-time Updates**: Live monitoring via WebSocket
- **Mobile Friendly**: Works on tablets and phones

### Advanced Features:
- **Message Content Editing**: Set system/user/assistant prompts
- **Interview Settings**: Configure intro/outro messages
- **System Controls**: Maintenance mode, log saving, database operations
- **Professional UI**: Modern, responsive design with error handling

## 🔄 Alternative: Use Existing Admin

If you prefer the original interface:

```cmd
python admin_fe.py
```

This starts the Gradio admin interface on port 9666.

## 📞 Support

If you encounter issues:

1. **Node.js Issues**: 
   - Restart command prompt after installation
   - Check if Node.js is in PATH: `where node`
   - Try running commands with full path

2. **Build Issues**:
   - Delete `frontend\node_modules` and `package-lock.json`
   - Run `npm install` again
   - Check for error messages in the output

3. **Server Issues**:
   - Check if port 8998 is available: `netstat -ano | findstr 8998`
   - Try different port: `uvicorn wa:app --port 8999`

4. **Admin Access Issues**:
   - Verify admin key from `config.toml`
   - Check console for JavaScript errors
   - Ensure browser allows mixed content if needed

## 🎉 Success Indicators

✅ **Setup Successful When**:
- `npm install` completes without errors
- `npm run build` creates `frontend/dist` folder  
- Server starts without errors
- Login page appears at `http://192.168.30.50:8998`
- Admin dashboard loads after login

The Vue.js admin interface provides a massive upgrade to your MayBot management experience with real-time updates, responsive design, and professional controls while maintaining full compatibility with your existing system!