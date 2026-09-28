# Webhooks

Webhooks notify your systems in real time when events happen in Acme Cloud — deploys, build failures, scaling events, and more.

## Creating a webhook

Go to **Project → Settings → Webhooks** and click **Add Webhook**. Enter the HTTPS URL that should receive events and select which events to subscribe to. We deliver JSON payloads via HTTP POST.

## Supported events

- `deploy.started` — a deployment began
- `deploy.succeeded` — a deployment completed successfully
- `deploy.failed` — a deployment failed (includes the build log excerpt)
- `service.scaled` — autoscaling changed the replica count
- `domain.verified` — a custom domain finished verification

## Verifying signatures

Every webhook request includes an `X-Acme-Signature` header: an HMAC-SHA256 of the raw request body, computed with your webhook signing secret. Always verify this signature before trusting a payload. You can find your signing secret on the webhook details page and rotate it at any time.

## Retries and timeouts

Your endpoint must respond within 10 seconds with a 2xx status code. If delivery fails, we retry with exponential backoff for up to 24 hours (8 attempts), then mark the event as undelivered. Failed deliveries appear in the webhook delivery log.

## Testing webhooks

Use the **Send Test Event** button on the webhook details page to fire a sample `deploy.succeeded` payload at your endpoint without triggering a real deploy.
