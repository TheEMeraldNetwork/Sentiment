# 🔒 Security Documentation

This document outlines the security practices and sensitive information handling for the Tigro Financial Sentiment Analysis Pipeline.

## 🔑 Sensitive Information Overview

### API Keys and Credentials
The following sensitive information is used in this project:

1. **Finnhub API Key** - For financial news and market data
2. **NewsAPI Key** - For additional news sources  
3. **Gmail App Password** - For email reporting system
4. **Webhook Authentication Token** - For webhook service security

### Current Security Implementation

#### ✅ Properly Secured
- **API Keys**: Stored in `utils/config/api_keys.json` (excluded from git)
- **Gmail Credentials**: Not stored in code, configured separately
- **Git Exclusions**: `.gitignore` properly configured

#### ⚠️ Security Improvements Needed
- **Webhook Token**: Currently hardcoded in multiple files
- **Email Configuration**: Consider externalizing email settings

## 🛡️ Security Best Practices

### 1. API Keys Management

#### Current Setup
```json
// utils/config/api_keys.json (not tracked by git)
{
    "FINNHUB_KEY": "your-finnhub-api-key",
    "NEWSAPI_KEY": "your-newsapi-key"
}
```

#### Security Features:
- ✅ File excluded from git via `.gitignore`
- ✅ Template file provided for setup
- ✅ Environment variable fallback available
- ✅ Validation and error handling in place

### 2. Email Security

#### Gmail Integration
- **Authentication**: App-specific passwords (not main password)
- **Requirements**: 2-factor authentication enabled
- **Storage**: Credentials not stored in code repository
- **SMTP**: Secure connection using TLS/SSL

#### Configuration Example (not stored in git):
```python
email_config = {
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "email_address": "your-email@gmail.com",
    "app_password": "your-app-specific-password",
    "recipient_email": "recipient@email.com"
}
```

### 3. Webhook Security

#### Current Implementation
- **Authentication**: Bearer token-based authentication
- **Token**: `tigro_2025_secure` (hardcoded - needs improvement)
- **CORS**: Configured for GitHub Pages integration
- **Endpoints**: Protected with authentication checks

#### Security Concerns:
- ⚠️ Token is hardcoded in source files
- ⚠️ Token appears in multiple locations
- ⚠️ No token rotation mechanism

## 🔧 Security Improvements Recommended

### 1. Webhook Token Externalization
Move webhook token to configuration file:

```json
// utils/config/security_keys.json (add to .gitignore)
{
    "WEBHOOK_TOKEN": "tigro_2025_secure",
    "JWT_SECRET": "optional-jwt-secret-for-future"
}
```

### 2. Environment Variable Usage
```bash
# For production deployments
export WEBHOOK_TOKEN="tigro_2025_secure"
export GMAIL_APP_PASSWORD="your-app-password"
```

### 3. Enhanced Authentication
- Consider JWT tokens for webhook authentication
- Implement token rotation mechanism
- Add rate limiting for webhook endpoints

## 🚨 What NOT to Commit

### Never commit these files:
- `utils/config/api_keys.json`
- `utils/config/security_keys.json`
- `.env` files
- `credentials.json`
- `*.pem`, `*.key` files
- Any file containing passwords or secrets

### Current `.gitignore` Protection:
```gitignore
# Sensitive files
utils/config/api_keys.json
.env
*.pem
*.key
credentials.json
```

## 📋 Security Checklist

### Before Deployment:
- [ ] Verify all API keys are externalized
- [ ] Confirm `.gitignore` excludes sensitive files
- [ ] Test authentication mechanisms
- [ ] Validate CORS configuration
- [ ] Review webhook token security
- [ ] Check email configuration is not hardcoded

### Regular Security Maintenance:
- [ ] Rotate API keys periodically
- [ ] Update webhook tokens
- [ ] Review access logs
- [ ] Monitor for exposed credentials
- [ ] Update dependencies for security patches

## 🔍 Finding Exposed Secrets

### Search for potential secrets:
```bash
# Search for hardcoded passwords/tokens
grep -r "password\|token\|key\|secret" --include="*.py" .

# Check for API keys in code
grep -r "FINNHUB_KEY\|NEWSAPI_KEY" --include="*.py" .

# Look for email credentials
grep -r "smtp\|gmail\|email.*password" --include="*.py" .
```

## 🚀 Production Security Notes

### For Production Deployment:
1. Use environment variables instead of config files
2. Implement proper secrets management (AWS Secrets Manager, etc.)
3. Enable HTTPS for all webhook endpoints
4. Add proper logging and monitoring
5. Implement rate limiting and DDoS protection
6. Regular security audits and penetration testing

## 📞 Security Contact

If you discover a security vulnerability, please:
1. **DO NOT** create a public GitHub issue
2. Email security concerns privately
3. Allow time for fixes before public disclosure
4. Follow responsible disclosure practices

## 🔄 Current Security Status

### ✅ Implemented
- API keys externalized and protected
- Git exclusions configured
- Authentication mechanisms in place
- Secure email configuration

### ⚠️ Needs Improvement
- Webhook token hardcoded (multiple files)
- No token rotation mechanism
- Email configuration could be externalized
- Missing rate limiting on webhooks

### 🔮 Future Enhancements
- JWT token implementation
- OAuth2 authentication
- Secrets management service integration
- Enhanced monitoring and alerting

---

**Last Updated**: July 12, 2025  
**Security Review**: Regular reviews recommended every 90 days 