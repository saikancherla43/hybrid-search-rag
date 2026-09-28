# API Authentication

The Acme Cloud REST API lets you manage projects, services, and deployments programmatically. The base URL is `https://api.acmecloud.example/v1`.

## API keys

Create an API key in the dashboard under **Settings → API Keys**. Keys are scoped to a single project or to your whole account. Treat keys like passwords — store them in a secrets manager, never in source control. You can rotate a key at any time; the old key stops working immediately.

## Making authenticated requests

Pass your API key in the `Authorization` header using the Bearer scheme:

```
Authorization: Bearer ac_live_51H7x9...
```

All requests must use HTTPS. Requests without a valid key return `401 Unauthorized`.

## OAuth 2.0 for integrations

If you are building a public integration, use OAuth 2.0 instead of personal API keys. Register your application under **Settings → OAuth Apps** to get a client ID and secret. We support the authorization-code flow with PKCE. Scopes include `projects:read`, `projects:write`, `deployments:read`, and `deployments:write`.

## Rate limits

API keys are limited to 1,000 requests per minute per account. OAuth apps are limited to 500 requests per minute per installation. Exceeding the limit returns `429 Too Many Requests` with a `Retry-After` header in seconds.

## Revoking access

Revoke a compromised key instantly from **Settings → API Keys → Revoke**. Revoking an OAuth grant from **Settings → Authorized Apps** immediately invalidates its tokens. Audit logs record every key creation and revocation event.
