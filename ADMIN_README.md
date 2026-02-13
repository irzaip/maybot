# MayBot Admin Interface

A modern Vue.js admin interface for managing the MayBot WhatsApp chatbot system.

## Features

### 🎯 Core Functionality
- **Real-time Dashboard**: Live system monitoring with WebSocket updates
- **Conversation Management**: View, search, and manage all active conversations
- **Bulk Operations**: Apply settings to multiple conversations at once
- **Detailed Controls**: Persona, mode, type, intervals, and message management
- **Usage Management**: Control free tries, paid messages, and GPT access
- **Direct Communication**: Send messages directly to users
- **System Controls**: Maintenance mode, log saving, database operations

### 🛠️ Technical Features
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Real-time Updates**: WebSocket integration for live data
- **Modern UI**: Vue.js 3 with TypeScript and Tailwind-style CSS
- **Secure Access**: Admin key authentication using existing phone numbers
- **FastAPI Integration**: Seamlessly integrates with existing backend

## Setup Instructions

### Prerequisites
- Python 3.11+ with existing MayBot setup
- Node.js 16+ and npm for frontend building

### Installation

1. **Build the Admin Interface**:
   ```bash
   python build_admin.py
   ```
   This will:
   - Install frontend dependencies
   - Build the Vue.js application
   - Copy files to the static directory

2. **Start the Server**:
   ```bash
   uvicorn wa:app --host 192.168.30.50 --port 8998
   ```

3. **Access the Admin Panel**:
   ```
   http://192.168.30.50:8998/?admin_key=YOUR_ADMIN_PHONE
   ```
   
   Replace `YOUR_ADMIN_PHONE` with your admin number from `config.toml`:
   ```
   62895352277562@c.us
   ```

### Development Mode

For development, you can run the frontend separately:

1. **Start Backend**:
   ```bash
   uvicorn wa:app --host 192.168.30.50 --port 8998 --reload
   ```

2. **Start Frontend Development Server**:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

3. **Access Development Interface**:
   ```
   http://localhost:5173/?admin_key=YOUR_ADMIN_PHONE
   ```

## Usage Guide

### Dashboard Overview
- **System Status**: Shows online/offline status, maintenance mode
- **Statistics**: Active conversations, message counts, token usage
- **Quick Actions**: Refresh data, save logs, rebuild database

### Conversation Management
1. **Search Conversations**: Use the search bar to filter by user name, number, or settings
2. **Select Conversations**: Click checkboxes or individual conversations
3. **Bulk Operations**: 
   - Select multiple conversations
   - Choose persona/mode/type from dropdowns
   - Click "Apply Changes"

### Detailed Conversation Controls
Click on any conversation to see detailed controls:

#### Basic Information
- Edit user name and bot name
- View user number (read-only)

#### Conversation Settings
- **Persona**: Choose from 13 available personas (ASSISTANT, HRD, SALES_CS, etc.)
- **Mode**: Set conversation mode (CHITCHAT, ASK, INTERVIEW, etc.)
- **Type**: Configure conversation type (DEMO, FRIEND, GOLD, PLATINUM, ADMIN)
- **Interval**: Set timed response interval in seconds
- **Temperature**: Adjust AI response randomness (0.0-1.0)

#### Usage Limits
- **Free Tries**: Add more free tries with "Add" button
- **Paid Messages**: Increase paid message credits
- **Free GPT**: Toggle free GPT access on/off

#### Message Content
- **System Message**: Set the AI system prompt
- **User Message**: Pre-set user message context
- **Assistant Message**: Define assistant response template

#### Interview Settings
- **Intro Message**: Set greeting for interview mode
- **Outro Message**: Configure interview closing message

#### Quick Actions
- **Reset Channel**: Reset conversation to default settings
- **Test Send**: Send a test message to verify connectivity
- **Start Questions**: Begin interview questioning sequence
- **Reset Questions**: Clear all bot questions

#### Direct Communication
- Send custom messages directly to users
- Useful for support or announcements

## Security

### Admin Authentication
- Uses existing `ADMIN_NUMBER` list from `config.toml`
- Admin key passed as URL parameter
- All admin routes require valid admin key
- WebSocket connections also authenticated

### Recommended Practices
- Keep admin keys confidential
- Use HTTPS in production
- Regular backups of conversation database
- Monitor usage logs for unusual activity

## API Endpoints

The admin interface uses these new API endpoints (all require admin_key):

- `GET /api/admin/dashboard/stats` - Dashboard statistics
- `GET /api/admin/conversations` - List conversations with search
- `POST /api/admin/bulk/persona` - Bulk persona changes
- `POST /api/admin/bulk/convmode` - Bulk mode changes  
- `POST /api/admin/bulk/convtype` - Bulk type changes
- `WS /api/admin/ws` - WebSocket for real-time updates

## File Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── admin/          # Admin-specific components
│   │   └── common/         # Shared components
│   ├── views/              # Page components
│   ├── api/                # API client with axios
│   ├── stores/             # Pinia state management
│   ├── router/             # Vue Router configuration
│   ├── types/              # TypeScript type definitions
│   └── utils/             # Utility functions
├── public/                 # Static assets
└── dist/                   # Build output (copied to ../static/)
```

## Troubleshooting

### Common Issues

1. **"Admin access required" error**
   - Check that admin_key is in URL
   - Verify admin number is in config.toml ADMIN_NUMBER list

2. **"Static directory not found" warning**
   - Run `python build_admin.py` to build frontend
   - Ensure frontend directory exists

3. **WebSocket connection fails**
   - Check firewall settings
   - Verify admin_key parameter
   - Check console for specific error messages

4. **Build fails with npm error**
   - Ensure Node.js 16+ is installed
   - Try deleting `frontend/node_modules` and `package-lock.json`
   - Run `npm install` again

### Development Tips

- Use browser DevTools to monitor WebSocket messages
- Check Network tab for API call debugging
- Frontend hot reloads automatically in development mode
- Backend auto-reloads with `--reload` flag

## Integration Notes

The admin interface is designed to:
- **Complement** the existing Gradio admin interface
- **Enhance** with modern UI/UX and real-time updates  
- **Integrate** seamlessly with current MayBot architecture
- **Maintain** all existing functionality and API endpoints

No changes to existing conversation logic or database structure are required.

## Support

For issues or questions:
1. Check the browser console for JavaScript errors
2. Verify backend logs for API errors
3. Test with the existing admin_fe.py Gradio interface
4. Check that all requirements.txt dependencies are installed

Built with ❤️ using Vue.js 3, TypeScript, Pinia, and FastAPI.