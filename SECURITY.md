# Security Policy

## Supported Versions

| Version | Supported          | Security Status |
| ------- | ------------------ | --------------- |
| 1.0.1   | :white_check_mark: | Secure          |
| 1.0.0   | :x:                | Vulnerabilities |
| < 1.0   | :x:                | Not supported   |

## Known Vulnerabilities

### Fixed in v1.0.1 (2025-11-15)

| CVE | Package | Severity | Description | Status |
|-----|---------|----------|-------------|--------|
| CVE-2024-47874 | starlette | HIGH | DoS via multipart/form-data | ✅ Fixed |
| CVE-2025-54121 | starlette | MEDIUM | DoS with large files | ✅ Fixed |
| CVE-2024-47081 | requests | MEDIUM | .netrc credentials leak | ✅ Fixed |
| CVE-2025-8869 | pip | MEDIUM | Symlink extraction | ✅ Fixed |

## Vulnerability Scanning

This project uses **Trivy** for vulnerability scanning.

### Scan Docker image
```bash
trivy image votre-username/unit-converter-api:latest
```

### Scan requirements
```bash
trivy fs --scanners vuln requirements.txt
```

### CI/CD Integration

Security scanning is integrated in the CI/CD pipeline:
- Pre-build: Scan requirements.txt
- Post-build: Scan Docker image
- Fail on: HIGH or CRITICAL vulnerabilities

## Reporting a Vulnerability

If you discover a security vulnerability, please:

1. **DO NOT** open a public issue
2. Email: toumi.mahdi.cr7@gmail.com
3. Include:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

Response time: Within 48 hours

## Security Best Practices

### When using this image:

✅ **DO:**
- Use specific version tags (`1.0.1` not `latest` in production)
- Keep your deployment updated
- Scan images regularly
- Use secrets management for sensitive data
- Run containers as non-root (default in this image)
- Set resource limits

❌ **DON'T:**
- Use `latest` tag in production
- Store secrets in environment variables
- Run as root user
- Expose unnecessary ports

### Docker Security

This image follows security best practices:
- ✅ Non-root user (UID 1000)
- ✅ Minimal base image (python:3.11-slim)
- ✅ Multi-stage build (no build tools)
- ✅ Health checks
- ✅ Regular dependency updates
- ✅ No hardcoded secrets

## Updates

Check for updates regularly:
- GitHub Releases: https://github.com/Mahdi-toumi/unit-converter-api/releases
- Docker Hub: https://hub.docker.com/r/toumimahdi/unit-converter-api

## Security Tools

We use:
- **Trivy**: Container and dependency scanning
- **Bandit**: Python SAST
- **Safety**: Python dependency checker
- **OWASP ZAP**: DAST

## Compliance

- OWASP Top 10 compliant
- CIS Docker Benchmark aligned
- NIST guidelines followed

## License

See [LICENSE](LICENSE) file.