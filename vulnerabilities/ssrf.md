# How I look for SSRF in real applications

This note describes my practical approach to identifying
Server-Side Request Forgery (SSRF) vulnerabilities
in web applications and APIs.

I focus on understanding **how the backend builds and performs outbound requests**.

---

## 1. Identifying SSRF Entry Points

I start by searching for parameters that influence backend HTTP requests.

Typical indicators:
- URL or host parameters
- API endpoints calling external services
- integrations (stock, delivery, payment, webhooks)
- file import / preview functionality

Example: stockApi=http://stock.weliketoshop.net:8080/product/stock/check?productId=6&storeId=1

This strongly suggests a server-side request.

---

## 2. Basic SSRF Validation

I first test whether I can control the destination of the request.

Example: stockApi=http://example.com

Then I attempt internal targets:
stockApi=http://localhost

stockApi=http://127.0.0.1

stockApi=http://127.0.0.1/admin

Observable indicators:
- response content changes
- connection errors
- timeout differences
- HTTP 500 responses

---

## 3. Internal Network Access Testing

After confirming outbound request control, I test access to internal services.

Common targets:

http://localhost

http://127.0.0.1

http://169.254.169.254

http://internal-service

Cloud metadata endpoints are always tested where applicable.

---

## 4. Blacklist-based Filter Bypass

If basic payloads are blocked, I test alternative representations.

### IP obfuscation

http://2130706433

http://017700000001

http://127.1

### DNS-based bypass

http://controlled-domain.example(resolves to 127.0.0.1)

### Encoding tricks
- URL encoding
- double URL encoding
- mixed case
- protocol switching (http → https)

---

## 5. Whitelist-based Filter Bypass

If the application enforces allowed hosts, I test parsing edge cases.

### Userinfo injection

https://allowed-host@evil-host

### Fragment confusipn

https://evil-host#allowed-host

### Subdomain tricks

https://allowed-host.evil-host

### URL encoding mismatches
Used when input validation and request execution differ.

---

## 6. SSRF via Open Redirect

If direct SSRF is restricted, I look for open redirects.

Example: /redirect?next=http://evil-host

Then chain it: stockApi=https://vulnerable-site/redirect?next=http://internal-host

This often bypasses strict host validation.

---

## 7. Blind SSRF Detection

If no response is returned, I test for blind SSRF.

Methods:
- time-based behavior
- DNS interaction
- external callbacks

I use an out-of-band interaction service to confirm:
- DNS resolution
- HTTP requests
- connection attempts

---

## 8. Non-obvious SSRF Surfaces

I also test SSRF in:

- HTTP headers (e.g. Referer)
- XML payloads (via XXE)
- partial URL construction
- webhook URLs
- file import / preview endpoints

Example:

Referer: http://internal-host/admin

---

## Notes

- SSRF often appears as a **logic vulnerability**
- I prioritize understanding URL parsing behavior
- Response timing is often more important than content
