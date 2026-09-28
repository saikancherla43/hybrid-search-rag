# Integrations

Acme Cloud connects with the tools your team already uses. Browse the full directory in the dashboard under **Integrations**.

## Git providers

GitHub, GitLab, and Bitbucket integrations enable automatic deploys on push, plus preview deployments for pull requests. Each PR gets its own ephemeral URL that is torn down when the PR closes.

## Monitoring and alerting

Send metrics and logs to Datadog, New Relic, or Grafana Cloud with one-click integrations. You can also stream structured JSON logs to any HTTPS endpoint. Configure alert thresholds in **Project → Monitoring** — alerts fire via email, Slack, or PagerDuty.

## Notifications

Connect Slack or Microsoft Teams to get deploy notifications in a channel of your choice. Choose which events notify: deploy succeeded, deploy failed, and scaling events are the most common picks.

## SSO and identity

Google Workspace and Okta SSO are available on Growth and Scale plans; SAML-based providers (Azure AD, OneLogin) require Scale. Enforce SSO for all team members in **Settings → Security**.

## Databases

Provision managed PostgreSQL, Redis, or MySQL from the dashboard — connection strings are injected as environment variables automatically. Backups run daily and are retained for 30 days (90 days on Scale). You can also connect an external database over TLS.

## CI/CD

Use our GitHub Action or the REST API to trigger deploys from your existing CI pipeline. The `deploy.failed` webhook event pairs well with CI status checks to block merges on broken builds.
