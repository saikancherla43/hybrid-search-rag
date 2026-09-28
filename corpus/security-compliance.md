# Security & Compliance

Security is built into every layer of Acme Cloud. This page summarizes our certifications, encryption practices, and your responsibilities.

## Certifications

Acme Cloud is SOC 2 Type II certified and ISO 27001 certified. Scale-plan customers can request our audit reports under NDA from the trust center at trust.acmecloud.example. We complete penetration tests annually with an independent firm.

## Encryption

All data is encrypted in transit with TLS 1.2 or higher, and at rest with AES-256. Database backups are encrypted with separate keys managed in a hardware security module (HSM). You can bring your own key (BYOK) on the Scale plan.

## Network isolation

Each project runs in its own VPC with strict network policies. Services cannot reach each other across projects unless you explicitly configure private networking. Public internet access is only via the managed load balancer.

## Your responsibilities

You are responsible for your application code, dependencies, and secrets. Rotate API keys regularly, keep dependencies patched, and never commit secrets to git. Enable SSO/SAML for your team on Growth and Scale plans, and require two-factor authentication for all members.

## Data retention and deletion

We retain deploy logs for 90 days and audit logs for 1 year. You can request full deletion of your account data at any time via **Settings → Danger Zone → Delete Account**; deletion completes within 30 days and is confirmed by email.

## Incident response

Our on-call team responds to security incidents 24/7. Report suspected vulnerabilities to security@acmecloud.example — we ask for 90 days of coordinated disclosure.
