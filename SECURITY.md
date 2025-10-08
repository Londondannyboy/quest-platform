# Security Policy

## 🔒 Supported Versions

We actively support the following versions with security updates:

| Version | Supported          |
| ------- | ------------------ |
| 2.2.x   | ✅ Yes             |
| 2.1.x   | ⚠️ Critical fixes only |
| 2.0.x   | ❌ No              |
| < 2.0   | ❌ No              |

## 🚨 Reporting a Vulnerability

We take the security of Quest seriously. If you believe you have found a security vulnerability, please report it to us as described below.

### ⚠️ Please DO NOT:

- Open a public GitHub issue for security vulnerabilities
- Disclose the vulnerability publicly before we've had a chance to address it
- Exploit the vulnerability beyond what is necessary to demonstrate it

### ✅ Please DO:

1. **Email us** at: security@quest.example.com
2. **Include** the following information:
   - Type of vulnerability
   - Full paths of source file(s) related to the vulnerability
   - Location of the affected source code (tag/branch/commit or direct URL)
   - Step-by-step instructions to reproduce the issue
   - Proof-of-concept or exploit code (if possible)
   - Impact of the vulnerability
   - Suggested fix (if you have one)

### 📅 Response Timeline

- **Initial Response:** Within 48 hours
- **Status Update:** Within 5 business days
- **Fix Timeline:** Depends on severity (see below)

### 🎯 Severity Levels

| Severity | Description | Response Time | Examples |
|----------|-------------|---------------|----------|
| **Critical** | Immediate risk to production | 24-48 hours | SQL injection, RCE, auth bypass |
| **High** | Significant security impact | 1 week | XSS, CSRF, data exposure |
| **Medium** | Limited security impact | 2-4 weeks | Info disclosure, weak crypto |
| **Low** | Minimal security impact | Next release | Security best practices |

## 🔐 Security Measures

Quest implements the following security measures:

### Database Security

- ✅ Role-separated database users (least privilege)
- ✅ SSL/TLS required for all connections
- ✅ Parameterized queries (no SQL injection)
- ✅ IP whitelist for database access
- ✅ Daily automated backups

### API Security

- ✅ Rate limiting (100 req/min per IP)
- ✅ CORS whitelist (*.quest domains only)
- ✅ API key authentication
- ✅ Input validation and sanitization
- ✅ Output encoding to prevent XSS

### Infrastructure Security

- ✅ Secrets stored in environment variables
- ✅ No credentials in code or version control
- ✅ Regular security updates
- ✅ Vulnerability scanning (Trivy)
- ✅ Network isolation between services

### Content Security

- ✅ Content sanitization (DOMPurify)
- ✅ Content-Security-Policy headers
- ✅ No inline scripts
- ✅ Subresource Integrity (SRI)

## 🛡️ Known Security Considerations

### AI-Generated Content

- **Risk:** AI models may generate biased or inappropriate content
- **Mitigation:** Human-in-the-loop review for articles scoring <85
- **Monitoring:** Quality scores tracked in database

### Third-Party APIs

- **Risk:** External API compromises or data leaks
- **Mitigation:** 
  - API keys rotated quarterly
  - Exponential backoff to prevent abuse
  - Cost circuit breakers
  - No PII sent to AI APIs

### User-Uploaded Content

- **Status:** Not currently supported
- **Future:** Will implement strict validation when needed

## 📊 Security Audits

### Internal Audits

- **Frequency:** Quarterly
- **Last Audit:** October 2025
- **Next Audit:** January 2026

### External Audits

- **Status:** Planned for Q1 2026
- **Scope:** Full application security assessment

## 🔄 Security Updates

### Subscribing to Updates

To receive security updates:
1. Watch this repository on GitHub
2. Subscribe to our security mailing list: security-updates@quest.example.com
3. Follow our [status page](https://status.quest.example.com)

### Security Advisories

We publish security advisories through:
- GitHub Security Advisories
- Email notifications to subscribers
- Status page announcements

## ✅ Responsible Disclosure

We believe in responsible disclosure and will:

1. **Acknowledge** your report within 48 hours
2. **Investigate** and provide regular updates
3. **Fix** the vulnerability as quickly as possible
4. **Credit** you in our security advisory (if desired)
5. **Notify** affected users if necessary

### Hall of Fame

We maintain a Hall of Fame for security researchers who have helped make Quest more secure:

<!-- Hall of Fame will be updated here -->

*Be the first to contribute!*

## 🎁 Bug Bounty Program

**Status:** Under consideration for 2026

We're evaluating a bug bounty program with rewards for:
- Critical vulnerabilities: $500-$2000
- High severity: $200-$500
- Medium severity: $50-$200
- Low severity: Recognition + Swag

## 📚 Security Resources

### For Developers

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [CWE Top 25](https://cwe.mitre.org/top25/)
- [Security Best Practices](./docs/SECURITY_BEST_PRACTICES.md)

### For Users

- [Account Security Guide](./docs/USER_SECURITY.md)
- [Privacy Policy](./docs/PRIVACY.md)
- [Terms of Service](./docs/TERMS.md)

## 📞 Contact

For security-related questions or concerns:

- 🔒 **Security Team:** security@quest.example.com
- 🚨 **Emergency:** Use email with "[URGENT]" in subject
- 💬 **General Questions:** support@quest.example.com

---

**Last Updated:** October 7, 2025  
**Version:** 2.2
