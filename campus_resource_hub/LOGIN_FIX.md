# Login Issue - Diagnosis and Fix

## Problem Identified

Users were unable to log in due to two issues:

1. **Login Form Template Issue** (FIXED)
   - The login template was using plain HTML inputs instead of WTForms fields
   - CSRF token was not being included properly
   - Form validation errors were not being displayed

2. **Admin User Creation Bug** (FIXED)
   - When creating users through the admin panel without a password, the system set `password_hash` to an empty string `''`
   - Empty password hashes cannot be verified, causing login to fail
   - This has been fixed to require a password when creating new users

## Fixes Applied

### 1. Login Template (`src/views/templates/login.html`)
- ✅ Changed to use WTForms field rendering (`{{ form.email() }}`, `{{ form.password() }}`)
- ✅ Fixed CSRF token to use `{{ form.hidden_tag() }}`
- ✅ Added error message display for form validation errors
- ✅ Added flash message display for login errors

### 2. Login Controller (`src/controllers/auth_controller.py`)
- ✅ Added comprehensive error handling
- ✅ Added checks for missing password hashes
- ✅ Added checks for suspended/inactive accounts
- ✅ Added better error messages
- ✅ Added form validation error display

### 3. Admin User Creation (`src/controllers/admin_controller.py`)
- ✅ Fixed to require password when creating new users
- ✅ Prevents creating users with empty password hashes

## How to Fix Existing Users

If you have existing users with empty or invalid password hashes, use these tools:

### Option 1: Check User Accounts
```bash
python check_users.py
```
This will show all users and indicate which ones have password issues.

### Option 2: Reset User Password
```bash
python reset_user_password.py <email> <new_password>
```
Example:
```bash
python reset_user_password.py admin@campus.edu newpassword123
```

### Option 3: Re-seed Database
If you want to start fresh with test users:
```bash
python seed_data.py
```

This creates users with known passwords:
- **Admin**: `admin@campus.edu` / `admin123`
- **Student 1**: `student1@campus.edu` / `student123`
- **Student 2**: `student2@campus.edu` / `student123`
- **Staff 1**: `staff1@campus.edu` / `staff123`
- **Staff 2**: `staff2@campus.edu` / `staff123`

## Testing Login

1. **Start the application:**
   ```bash
   python run.py
   ```

2. **Navigate to login page:**
   - Go to `http://localhost:5000/auth/login`

3. **Try logging in:**
   - Use email and password from seed data or reset password
   - Check for error messages if login fails

4. **Check browser console:**
   - Open browser developer tools (F12)
   - Check Console tab for JavaScript errors
   - Check Network tab for failed requests

## Common Issues and Solutions

### "Invalid email or password"
- **Cause**: User doesn't exist, password is wrong, or password_hash is empty/invalid
- **Solution**: 
  - Verify user exists: `python check_users.py`
  - Reset password: `python reset_user_password.py <email> <new_password>`
  - Check that you're using the correct email (not username)

### "Account error: No password set"
- **Cause**: User was created without a password (empty password_hash)
- **Solution**: Reset the password using `reset_user_password.py`

### "Your account has been suspended"
- **Cause**: User's `is_suspended` flag is True
- **Solution**: Use admin panel to unsuspend the user, or update database directly

### "Your account has been deactivated"
- **Cause**: User's `is_active` flag is False
- **Solution**: Use admin panel to activate the user, or update database directly

### Form validation errors
- **Cause**: CSRF token missing or form fields invalid
- **Solution**: 
  - Clear browser cache and cookies
  - Make sure you're using the updated login template
  - Check that SECRET_KEY is set in your environment

## Verification Steps

1. ✅ Login template uses WTForms fields
2. ✅ CSRF token is included via `hidden_tag()`
3. ✅ Error messages are displayed
4. ✅ Admin user creation requires password
5. ✅ Login controller has proper error handling

## Next Steps

1. Run `python check_users.py` to see which users have issues
2. Reset passwords for affected users using `reset_user_password.py`
3. Try logging in again
4. If still having issues, check the browser console and server logs for specific error messages

