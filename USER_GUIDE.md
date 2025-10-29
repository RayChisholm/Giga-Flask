# Zendesk Bulk Operations Tool - User Guide

Welcome! This guide will help you install, set up, and use the Zendesk Bulk Operations Tool.

---

## What is This Tool?

The Zendesk Bulk Operations Tool is a modern web application that helps you perform bulk actions on your Zendesk account. Instead of manually updating tickets one by one, you can use this tool to:

- Search for macros containing specific text
- Export results to CSV or JSON format
- Apply macros to multiple tickets at once (coming soon)
- Manage tags across multiple tickets (coming soon)
- And much more!

The tool features:
- 🎨 **Modern, responsive design** that works on desktop and mobile
- ⚡ **Fast and intuitive** interface with loading indicators
- ⌨️ **Keyboard shortcuts** for power users
- 📊 **Result statistics** and visual dashboards
- 💾 **Export functionality** for data analysis
- ✅ **Real-time validation** to catch errors early

The tool is designed to save you time and reduce repetitive work.

---

## System Requirements

Before you begin, make sure you have:

- **A computer** running macOS, Windows, or Linux
- **Python 3.8 or higher** installed (check by running `python3 --version` in your terminal)
- **A Zendesk account** with admin access
- **A Zendesk API token** (we'll show you how to get this)

---

## Installation

### Step 1: Download the Project

If you received this project as a folder, simply navigate to it in your terminal:

```bash
cd "path/to/Giga Flask"
```

### Step 2: Create a Virtual Environment

This keeps the project's dependencies separate from your system Python:

```bash
python3 -m venv venv
```

### Step 3: Activate the Virtual Environment

**On Mac/Linux:**
```bash
source venv/bin/activate
```

**On Windows:**
```bash
venv\Scripts\activate
```

You should see `(venv)` appear at the beginning of your terminal prompt.

### Step 4: Install Dependencies

```bash
pip install -r requirements.txt
```

This will install all the necessary packages. It may take a minute or two.

### Step 5: Initialize the Database

```bash
python init_database.py
```

You should see:
```
Database tables created successfully!
Default admin user created:
  Username: admin
  Password: admin123
  IMPORTANT: Change this password after first login!
```

---

## Starting the Application

To start the application:

```bash
python run.py
```

You should see output like:
```
Registered tool: Search Macros (macro-search)
 * Serving Flask app 'app'
 * Debug mode: on
 * Running on http://127.0.0.1:5000
```

**Keep this terminal window open!** The application is now running.

---

## First Time Setup

### Step 1: Log In

1. Open your web browser
2. Go to: **http://127.0.0.1:5000**
3. You'll see the login page
4. Enter the default credentials:
   - **Username**: `admin`
   - **Password**: `admin123`
5. Click "Sign In"

### Step 2: Change Your Password (Recommended)

After logging in with the default credentials, you should create a new admin user with a secure password:

1. Click **"Admin"** in the top navigation bar
2. Click **"Manage Users"**
3. Click **"Create User"**
4. Fill in the form:
   - Choose a unique username
   - Enter your email
   - Create a strong password
   - Select **"Admin"** as the role
   - Check the **"Active"** box
5. Click **"Save User"**
6. Log out (click your username in the top right, then "Logout")
7. Log back in with your new credentials

### Step 3: Configure Zendesk

To use the tools, you need to connect your Zendesk account:

#### Getting Your Zendesk API Token

1. Log into your **Zendesk** account
2. Click the **Admin** icon (gear icon) in the sidebar
3. Go to **Admin Center**
4. Navigate to: **Apps and integrations > APIs > Zendesk API**
5. Under "Settings", click **"Add API token"**
6. Enter a description like "Bulk Operations Tool"
7. Click **"Create"**
8. **Copy the API token** (you won't be able to see it again!)

#### Configuring the Tool

1. In the Bulk Operations Tool, click **"Admin"** in the top navigation
2. Click **"Manage Settings"** (or "Zendesk Configuration")
3. Fill in the form:
   - **Zendesk Subdomain**: Your subdomain (e.g., "mycompany" if your URL is mycompany.zendesk.com)
   - **Email**: The email address associated with your Zendesk account
   - **API Token**: Paste the token you copied earlier
4. Click **"Save Settings"**
5. Click **"Test Connection"** to verify everything works

If the connection is successful, you'll see a green success message!

---

## Using the Tool

### Dashboard Overview

After logging in, you'll see the **Dashboard** which displays all available tools organized by category.

Each tool card shows:
- **Tool name**
- **Brief description**
- **Access level** (Admin badge if admin-only)
- **Launch button**

### Using a Tool

Let's walk through using the **Macro Search** tool as an example:

1. **Launch the Tool**:
   - From the Dashboard, click **"Search Macros"**

2. **Fill in the Form**:
   - Enter a search term (e.g., "urgent" or "priority")
   - Read the help text below the field if you need guidance

3. **Execute the Tool**:
   - Click **"Execute Tool"**
   - Wait for the results (may take a few seconds)

4. **View Results**:
   - Results appear below the form
   - A success/error message tells you what happened
   - Data is displayed in an easy-to-read table

5. **Take Action**:
   - For Macro Search results, you can click the "View" button to open each macro in Zendesk
   - Some tools may offer export options (CSV, JSON)

### Navigating Back

- Click **"Dashboard"** in the navigation bar to return to the tool list
- Click **"Cancel"** on any tool page to go back without executing
- Press **ESC** key to go back (keyboard shortcut)

### Exporting Results

Many tools support exporting results for further analysis:

1. **After running a tool** and seeing results, look for the green **"Export"** button in the top-right corner of the results section
2. **Click the Export dropdown** to see available formats:
   - **CSV**: Perfect for Excel or Google Sheets
   - **JSON**: Ideal for developers or data processing
3. **Click your preferred format** - the file will download automatically
4. The filename includes the search term for easy identification (e.g., `macro_search_urgent.csv`)

**Tips**:
- You can export results multiple times without re-running the tool
- Export is only available after successfully executing a tool
- Not all tools support export (check for the Export button)

### Keyboard Shortcuts

Power users can navigate faster with these macOS-optimized keyboard shortcuts:

| Shortcut | Action |
|----------|--------|
| **⌘K** | Go to Dashboard (Home) |
| **⌘⇧A** | Go to Admin Panel (if you're an admin) |
| **⌘⇧D** | Toggle Dark Mode |
| **⌘/** | Focus on Search Input |
| **⌘↵** | Submit Active Form |
| **ESC** | Go back / Cancel |

**Note**: All shortcuts use the Command (⌘) key. Keyboard shortcuts are shown in the footer of every page.

### Dark Mode

The application includes a built-in dark mode for comfortable viewing in low-light environments.

**How to Toggle Dark Mode**:
1. **Click the moon/sun icon** in the navigation bar (top-right)
2. **Use the keyboard shortcut**: Press **⌘⇧D**

**Features**:
- **Persistent**: Your dark mode preference is saved and remembered across sessions
- **System-aware**: Automatically detects your macOS system preference on first visit
- **Smooth transitions**: Theme changes smoothly without page reload
- **Comprehensive**: Dark mode styling applies to all pages, forms, tables, and components

**Tips**:
- Dark mode is ideal for extended use and reduces eye strain
- The toggle icon changes: 🌙 (moon) for light mode, ☀️ (sun) for dark mode
- Your preference syncs across all tabs automatically

### Understanding Results

When you run a tool, you'll see:

1. **Statistics Cards** (top of results):
   - Total count of items found
   - Breakdown by status (e.g., Active/Inactive)
   - Visual indicators with colors

2. **Results Table**:
   - Detailed information about each item
   - Action buttons (View, Edit, etc.)
   - Sortable columns (click headers)

3. **Success/Error Messages**:
   - Green alert = Success
   - Red alert = Error
   - Yellow alert = Warning
   - Messages auto-dismiss after 5 seconds

---

## Admin Functions

If you're an administrator, you have access to additional features:

### User Management

**To Create a New User**:
1. Go to **Admin > User Management**
2. Click **"Create User"**
3. Fill in the form:
   - Username (unique)
   - Email address
   - Password
   - Role (Admin or User)
   - Active status
4. Click **"Save User"**

**User Roles**:
- **Admin**: Full access to all features, user management, and settings
- **User**: Can use tools but cannot access admin panel

**To Edit a User**:
1. Go to **Admin > User Management**
2. Click **"Edit"** next to the user
3. Update any fields (leave password blank to keep current password)
4. Click **"Save User"**

**To Delete a User**:
1. Go to **Admin > User Management**
2. Click **"Delete"** next to the user
3. Confirm the deletion

**Note**: You cannot delete your own account.

### Viewing Registered Tools

As an admin, you can see all registered tools in the system:

1. Go to **Admin > Registered Tools**
2. You'll see a list of all available tools with:
   - Tool name and slug
   - Description
   - Access level (Admin Only or All Users)
   - Link to open the tool

### Updating Zendesk Settings

1. Go to **Admin > Zendesk Configuration**
2. Update any credentials
3. Click **"Save Settings"**
4. Test the connection to verify

**Security Note**: Your API token is stored securely. Never share your credentials with anyone.

---

## Available Tools

### 1. Search Macros

**Category**: Macros
**Access**: All Users
**Export**: ✅ CSV & JSON

**What it does**: Searches through all your Zendesk macros to find ones that contain a specific word or phrase in their actions.

**Use cases**:
- Find all macros that set a specific field
- Locate macros that mention a certain tag
- Identify macros that need updating
- Audit your macros for compliance
- Generate reports of macro usage

**How to use**:
1. Enter your search term (minimum 2 characters)
2. Click "Execute Tool"
3. **View Statistics** at the top:
   - Total macros found
   - Number of active macros
   - Number of inactive macros
4. **Review the results table** showing:
   - Macro title
   - Active status (color-coded badge)
   - Matching actions
   - Link to view in Zendesk
5. **Export results** (optional):
   - Click the green "Export" button
   - Choose CSV or JSON format
   - File downloads automatically

**Features**:
- ⚡ Fast search across all macros
- 📊 Visual statistics dashboard
- 💾 Export to CSV or JSON
- 🔍 Case-insensitive search
- 🎯 Highlights matching actions

---

### 2. Apply Macro to View

**Category**: Macros
**Access**: Admin Only ⚠️
**Export**: ✅ CSV & JSON

**What it does**: Applies a selected macro to all tickets in a specified Zendesk view. This is a powerful bulk operation tool with built-in safety features.

**Use cases**:
- Apply standard responses to multiple tickets at once
- Bulk update ticket fields via macro actions
- Standardize ticket handling across a view
- Close or resolve multiple tickets with consistent actions
- Automate repetitive macro applications

**How to use**:
1. **Select a View**: Choose the Zendesk view containing the tickets you want to update
2. **Select a Macro**: Choose which macro to apply (only active macros are shown)
3. **Set Ticket Limit**: Specify the maximum number of tickets to process
   - Recommended: Start with 10-50 for testing
   - Maximum allowed: 500 (process in batches for larger operations)
4. **Dry Run Option** (Recommended for first use):
   - Check the "Dry Run" box to preview which tickets will be affected
   - No changes are made in dry run mode
   - Review the preview, then uncheck and re-submit to apply
5. **Execute**: Click "Execute Tool" to run

**Results Display**:
- **Statistics Cards** showing:
  - Total tickets processed
  - Successful applications
  - Failed applications
  - Success rate percentage
- **Operation Details**: View and macro information
- **Ticket Lists**:
  - Successful: Tickets that were updated
  - Failed: Tickets with errors (if any)

**Safety Features**:
- **Admin Only**: Requires administrator privileges
- **Dry Run Mode**: Preview before making changes
- **Ticket Limit**: Maximum 500 tickets per execution
- **Rate Limiting**: 1-second delay between API calls to avoid hitting Zendesk limits
- **Auto-Retry**: Automatically retries on rate limit errors
- **Detailed Logging**: See exactly which tickets succeeded or failed
- **Export Results**: Keep records of bulk operations

**Important Notes**:
- ⚠️ This tool makes real changes to tickets. Always test with a small batch first
- 💡 Use dry run mode before your first actual run to confirm the right tickets
- 🔄 Rate limiting means larger batches take longer (500 tickets ≈ 8-10 minutes)
- 📊 Export results for audit trails and documentation
- ⚡ For operations over 500 tickets, run multiple batches

**Best Practices**:
1. **Always start with dry run** to preview affected tickets
2. **Test with small batches** (10-20 tickets) before larger operations
3. **Export results** for record-keeping
4. **Process in batches** if you have more than 500 tickets
5. **Review failed tickets** if any errors occur
6. **Coordinate with your team** before bulk operations on shared views

---

## Troubleshooting

### Problem: Can't Access the Application

**Solution**:
- Make sure the server is running (check your terminal)
- Verify you're using the correct URL: http://127.0.0.1:5000
- Try refreshing the page
- Check that nothing else is using port 5000

### Problem: "Invalid username or password"

**Solution**:
- Double-check you're using the correct credentials
- Remember: usernames and passwords are case-sensitive
- If you forgot your password, an admin can reset it or you can create a new user

### Problem: "Zendesk credentials not configured"

**Solution**:
- Go to Admin > Zendesk Configuration
- Enter your credentials
- Make sure you're using the correct subdomain (without ".zendesk.com")
- Test the connection

### Problem: "Connection failed" when testing Zendesk

**Possible causes**:
- Incorrect subdomain (should be just "mycompany", not "mycompany.zendesk.com")
- Wrong email address
- Invalid API token
- API token was deactivated in Zendesk
- Network/firewall issues

**Solution**:
- Verify all credentials in Zendesk
- Generate a new API token if needed
- Check your internet connection

### Problem: Tool execution takes too long

**Solution**:
- Some operations process many items and can take time
- Large Zendesk accounts may have slower response times
- Be patient and don't close the browser
- If it takes more than 5 minutes, refresh and try again

### Problem: Results are empty

**Solution**:
- Verify your search criteria are correct
- Make sure the data exists in Zendesk
- Try a broader search term
- Check that your API credentials have the necessary permissions

---

## Tips & Best Practices

### For All Users

1. **Test First**: Before running bulk operations (when available), test on a small dataset first
2. **Verify Results**: Always review results before taking further action
3. **Bookmark the URL**: Add http://127.0.0.1:5000 to your bookmarks
4. **Log Out**: Log out when finished, especially on shared computers

### For Administrators

1. **Regular Backups**: Back up the database file (`instance/app.db`) regularly
2. **User Cleanup**: Deactivate users who no longer need access instead of deleting them
3. **Monitor Tool Usage**: Check which tools are being used most
4. **Test Configuration Changes**: Use "Test Connection" after updating Zendesk settings
5. **Security**: Use strong passwords and change default credentials immediately

### For Power Users

1. **Learn Keyboard Shortcuts**: Tab through form fields for faster input
2. **Multiple Tabs**: Open tools in multiple browser tabs to work on several tasks
3. **Save Results**: Export results when available for record-keeping
4. **Combine Tools**: Use multiple tools together for complex workflows (when more tools are added)

---

## FAQ

### Q: Can multiple people use this tool at the same time?

**A**: Yes! Multiple users can log in and use the tool simultaneously. Each user has their own session.

### Q: Will this tool modify my Zendesk data?

**A**: The current "Search Macros" tool only reads data - it doesn't modify anything. Future tools that modify data will have clear warnings and confirmation steps.

### Q: Can I use this tool with multiple Zendesk accounts?

**A**: Currently, the tool supports one Zendesk account at a time. You can change the configured account in Admin > Zendesk Configuration.

### Q: Is my data secure?

**A**: The tool runs locally on your computer and communicates directly with Zendesk's API. Your credentials are stored in a local database file on your machine. Always keep your API token confidential.

### Q: Can I add my own tools?

**A**: If you have development experience, yes! See the `PROJECT_PLAN.md` and `CLAUDE_CONTEXT.md` files for technical documentation on adding new tools.

### Q: What happens if I close the terminal?

**A**: The application will stop running. You'll need to restart it using `python run.py`.

### Q: Can I run this on a server?

**A**: Yes, but additional configuration is needed for production deployment. The current setup is designed for local/development use.

### Q: How do I update to a newer version?

**A**: If you receive updated files, replace the old files, activate your virtual environment, run `pip install -r requirements.txt` to update dependencies, and restart the application.

---

## Getting Help

If you encounter issues not covered in this guide:

1. **Check the Error Message**: Error messages usually indicate what went wrong
2. **Check the Terminal**: The terminal running the application may show additional error details
3. **Review This Guide**: Search this document for keywords related to your issue
4. **Check Your Zendesk**: Verify your Zendesk account settings and permissions
5. **Contact Your Administrator**: If you're not an admin, reach out to whoever set up the tool

---

## Shutting Down the Application

When you're done using the tool:

1. Go to the terminal window running the application
2. Press **Ctrl+C** (on both Mac and Windows)
3. Wait for the server to shut down
4. You can now close the terminal

To start it again later, just run `python run.py` (make sure your virtual environment is activated first).

---

## Quick Reference

### Starting the Application

```bash
cd "path/to/Giga Flask"
source venv/bin/activate    # Mac/Linux
venv\Scripts\activate       # Windows
python run.py
```

### Default Login

- **URL**: http://127.0.0.1:5000
- **Default Username**: admin
- **Default Password**: admin123
- **⚠️ Change these immediately after first login!**

### Important URLs

- **Dashboard**: http://127.0.0.1:5000/
- **Login**: http://127.0.0.1:5000/auth/login
- **Admin Panel**: http://127.0.0.1:5000/admin

---

## What's Next?

Now that you're set up, you can:

1. ✅ Change your admin password
2. ✅ Configure your Zendesk credentials
3. ✅ Try the Macro Search tool
4. ✅ Create additional user accounts for your team
5. ✅ Explore the admin panel
6. 📅 Watch for new tools being added!

Current available tools:
- ✅ Search Macros
- ✅ Apply Macro to View (Admin only)

More tools coming soon:
- Bulk tag management (add/remove tags from view tickets)
- Bulk ticket deletion with safety checks
- Advanced ticket search features
- And more!

---

**Happy bulk operating! 🚀**

*Last updated: 2025-10-27*
