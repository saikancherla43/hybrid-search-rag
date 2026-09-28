# Troubleshooting Common Errors

This guide covers the most frequent errors customers hit on Acme Cloud and how to fix them.

## Build failed: command exited with code 1

The build command failed. Open the deploy log in the dashboard and look at the last 50 lines — the actual error is usually a missing dependency or a typo in the build command. Common fix: make sure your lockfile (`package-lock.json`, `requirements.txt`, etc.) is committed, and that the build command in **Service → Settings** matches your project.

## Error 502: Bad Gateway after deploy

Your service started but is not accepting connections. Check that your app binds to `0.0.0.0` and the port in the `$PORT` environment variable — binding to `localhost` or a hardcoded port is the #1 cause. Also verify the health check path returns 200.

## Error 429: Too Many Requests

You hit the API rate limit (1,000 requests/min per account, 500 for OAuth apps). Back off and retry after the number of seconds in the `Retry-After` header. If you need a higher limit, contact support about a Scale plan.

## Deploy stuck in "Building" for over 20 minutes

Cancel the deploy and retry. If it happens repeatedly, your build is likely downloading large dependencies on every run — add a build cache in **Service → Settings → Build Cache**, or split the build into smaller steps.

## Custom domain shows "Not secure"

DNS is probably still propagating, which can take up to 48 hours. Verify your CNAME record points to `cname.acmecloud.example`. If it has been over 48 hours, check **Domains → Status** for the specific verification error.

## Out of build minutes

Starter includes 1,000 build minutes/month and Growth includes 10,000. Check usage in **Billing → Usage**. You can buy extra minutes at $0.005/min or upgrade your plan.
