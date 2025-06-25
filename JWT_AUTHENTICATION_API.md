# JWT Authentication API Documentation

## Overview
This document describes the JWT authentication system with SMS verification using Kavenegar for multi-device authentication.

## Features
- ✅ SMS verification using Kavenegar API
- ✅ Multi-device authentication with JWT tokens
- ✅ Device management (view, revoke devices)
- ✅ Automatic token refresh
- ✅ Login notifications via SMS
- ✅ Secure token storage and validation

## API Endpoints

### 1. SMS Verification Request
**POST** `/accounts/sms-verification-request/`

Request SMS verification code to user's phone number.

**Request Body:**
```json
{
    "phone_number": "+989123456789"
}
```

**Response:**
```json
{
    "message": "کد تأیید ارسال شد.",
    "phone_number": "+989123456789"
}
```

### 2. JWT Login with SMS Verification
**POST** `/accounts/jwt-login/`

Login with SMS verification code and get JWT tokens.

**Request Body:**
```json
{
    "phone_number": "+989123456789",
    "verification_code": "123456",
    "device_info": {
        "device_name": "iPhone 12",
        "device_type": "mobile"
    }
}
```

**Response:**
```json
{
    "message": "ورود موفقیت‌آمیز بود.",
    "user": {
        "id": 1,
        "full_name": "علی احمدی",
        "phone_number": "+989123456789",
        "email": "ali@example.com",
        "is_phone_verified": true
    },
    "tokens": {
        "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
        "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
        "device_id": "550e8400-e29b-41d4-a716-446655440000",
        "device_name": "iPhone 12",
        "device_type": "mobile"
    }
}
```

### 3. Refresh JWT Token
**POST** `/accounts/jwt-refresh/`

Refresh access token using refresh token.

**Request Body:**
```json
{
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Response:**
```json
{
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

### 4. Get User Devices
**GET** `/accounts/devices/`

Get all active devices for the authenticated user.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:**
```json
{
    "devices": [
        {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "device_name": "iPhone 12",
            "device_type": "mobile",
            "is_active": true,
            "last_used": "2024-01-15T10:30:00Z",
            "created_at": "2024-01-10T09:00:00Z",
            "expires_at": "2024-01-17T09:00:00Z"
        }
    ],
    "total_devices": 1
}
```

### 5. Revoke Specific Device
**POST** `/accounts/revoke-device/`

Revoke a specific device token.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
    "device_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Response:**
```json
{
    "message": "دستگاه با موفقیت غیرفعال شد."
}
```

### 6. Logout
**POST** `/accounts/logout/`

Logout and optionally revoke all tokens.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
    "revoke_all": false
}
```

**Response:**
```json
{
    "message": "دستگاه فعلی غیرفعال شد."
}
```

## Device Types
- `mobile`: Mobile phones
- `tablet`: Tablets
- `desktop`: Desktop computers
- `web`: Web browsers
- `other`: Other devices

## Authentication Flow

### 1. User Registration/Login Flow
```
1. User enters phone number
2. System sends SMS verification code via Kavenegar
3. User enters verification code
4. System validates code and creates JWT tokens
5. User receives access and refresh tokens
6. User can access protected endpoints
```

### 2. Token Refresh Flow
```
1. Access token expires
2. Client sends refresh token
3. System validates refresh token
4. System issues new access and refresh tokens
5. Client continues with new tokens
```

### 3. Multi-Device Management
```
1. User logs in from multiple devices
2. Each device gets unique JWT tokens
3. User can view all active devices
4. User can revoke specific devices
5. User can revoke all devices on logout
```

## Error Responses

### Common Error Codes
- `400`: Bad Request (invalid data)
- `401`: Unauthorized (invalid/missing token)
- `403`: Forbidden (insufficient permissions)
- `404`: Not Found (resource not found)
- `500`: Internal Server Error

### Error Response Format
```json
{
    "error": "Error message in Persian",
    "details": "Additional error details"
}
```

## Security Features

### 1. Token Security
- Access tokens expire in 30 minutes
- Refresh tokens expire in 7 days
- Tokens are device-specific
- Automatic token rotation on refresh

### 2. Device Management
- Each device gets unique tokens
- Device tokens can be individually revoked
- Login notifications sent via SMS
- Device activity tracking

### 3. SMS Verification
- 6-digit verification codes
- 2-minute expiration time
- Rate limiting on SMS requests
- Secure code generation

## Usage Examples

### JavaScript/React Example
```javascript
// Request SMS verification
const requestSMS = async (phoneNumber) => {
    const response = await fetch('/accounts/sms-verification-request/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ phone_number: phoneNumber })
    });
    return response.json();
};

// Login with verification code
const login = async (phoneNumber, code, deviceInfo) => {
    const response = await fetch('/accounts/jwt-login/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            phone_number: phoneNumber,
            verification_code: code,
            device_info: deviceInfo
        })
    });
    return response.json();
};

// Use access token for authenticated requests
const getProtectedData = async (accessToken) => {
    const response = await fetch('/api/protected-endpoint/', {
        headers: {
            'Authorization': `Bearer ${accessToken}`
        }
    });
    return response.json();
};
```

### Python Example
```python
import requests

# Request SMS verification
def request_sms(phone_number):
    response = requests.post('/accounts/sms-verification-request/', json={
        'phone_number': phone_number
    })
    return response.json()

# Login with verification code
def login(phone_number, code, device_info):
    response = requests.post('/accounts/jwt-login/', json={
        'phone_number': phone_number,
        'verification_code': code,
        'device_info': device_info
    })
    return response.json()

# Use access token for authenticated requests
def get_protected_data(access_token):
    headers = {'Authorization': f'Bearer {access_token}'}
    response = requests.get('/api/protected-endpoint/', headers=headers)
    return response.json()
```

## Management Commands

### Cleanup Expired Tokens
```bash
# Clean up expired tokens
python manage.py cleanup_expired_tokens

# Dry run to see what would be cleaned up
python manage.py cleanup_expired_tokens --dry-run
```

## Configuration

### Settings Configuration
```python
# Kavenegar SMS Settings
KAVENEGAR_API_KEY = 'your_api_key_here'
KAVENEGAR_SENDER = 'your_sender_number'

# JWT Settings
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=30),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'UPDATE_LAST_LOGIN': True,
}
```

## Best Practices

### 1. Token Storage
- Store access tokens in memory (not localStorage)
- Store refresh tokens securely
- Implement automatic token refresh
- Handle token expiration gracefully

### 2. Security
- Use HTTPS in production
- Implement rate limiting
- Monitor for suspicious activity
- Regular token cleanup

### 3. User Experience
- Clear error messages in Persian
- Automatic SMS resend functionality
- Device management interface
- Login activity notifications

## Troubleshooting

### Common Issues

1. **SMS not received**
   - Check Kavenegar API key
   - Verify phone number format
   - Check SMS provider status

2. **Token validation errors**
   - Ensure correct Authorization header format
   - Check token expiration
   - Verify device token is active

3. **Device management issues**
   - Check device token permissions
   - Verify user ownership of device
   - Ensure device token exists

### Debug Mode
Enable debug mode in Django settings to get detailed error information:
```python
DEBUG = True
```

## Support

For technical support or questions about the JWT authentication system, please contact the development team. 