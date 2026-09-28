# Demo transcript — real runs

Backend: dense = all-MiniLM-L6-v2 (sbert); BM25 from scratch; hybrid = RRF fusion (k=60).
Run with: `ST_MODEL_DIR=<path-to-model> python demo/demo.py "<question>"`

---

## Run 1: "How much does the Growth plan cost per month?"

```
Query: How much does the Growth plan cost per month?

=== DENSE top-3 ===
  #1  score=0.5878  troubleshooting > Out of build minutes
       Starter includes 1,000 build minutes/month and Growth includes 10,000. Check usage in **Billing → Usage**. You can buy extra minutes at $0.005/min or upgrade your plan. ...
  #2  score=0.5698  pricing-plans > Annual billing
       Pay annually to save 20% on Growth seats. Scale contracts are annual by default. ...
  #3  score=0.5689  pricing-plans > Growth — $29/month per seat
       Growth is our most popular plan for production workloads. It includes 25 team seats, 1 TB of bandwidth per month, 10,000 build minutes per month, autoscaling, zero-downtime deploys, ...

=== BM25 top-3 ===
  #1  score=9.6977  pricing-plans > Growth — $29/month per seat
       Growth is our most popular plan for production workloads. It includes 25 team seats, 1 TB of bandwidth per month, 10,000 build minutes per month, autoscaling, zero-downtime deploys, ...
  #2  score=8.9646  pricing-plans > Starter — $0/month
       The Starter plan is free forever and ideal for side projects and evaluation. It includes 3 team seats, 100 GB of bandwidth per month, 1,000 build minutes per ...
  #3  score=6.7282  troubleshooting > Out of build minutes
       Starter includes 1,000 build minutes/month and Growth includes 10,000. Check usage in **Billing → Usage**. You can buy extra minutes at $0.005/min or upgrade your plan. ...

=== HYBRID top-3 ===
  #1  score=0.0323  troubleshooting > Out of build minutes
       Starter includes 1,000 build minutes/month and Growth includes 10,000. Check usage in **Billing → Usage**. You can buy extra minutes at $0.005/min or upgrade your plan. ...
  #2  score=0.0323  pricing-plans > Growth — $29/month per seat
       Growth is our most popular plan for production workloads. It includes 25 team seats, 1 TB of bandwidth per month, 10,000 build minutes per month, autoscaling, zero-downtime deploys, ...
  #3  score=0.0315  pricing-plans > Starter — $0/month
       The Starter plan is free forever and ideal for side projects and evaluation. It includes 3 team seats, 100 GB of bandwidth per month, 1,000 build minutes per ...

```

## Run 2: "What should I do if my deploy fails with a 502 Bad Gateway error?"

```
Query: What should I do if my deploy fails with a 502 Bad Gateway error?

=== DENSE top-3 ===
  #1  score=0.4220  troubleshooting > Deploy stuck in "Building" for over 20 minutes
       Cancel the deploy and retry. If it happens repeatedly, your build is likely downloading large dependencies on every run — add a build cache in **Service → Settings ...
  #2  score=0.4137  webhooks > Supported events
       - `deploy.started` — a deployment began - `deploy.succeeded` — a deployment completed successfully - `deploy.failed` — a deployment failed (includes the build log excerpt) - `service.scaled` — autoscaling ...
  #3  score=0.3695  troubleshooting > Build failed: command exited with code 1
       The build command failed. Open the deploy log in the dashboard and look at the last 50 lines — the actual error is usually a missing dependency or ...

=== BM25 top-3 ===
  #1  score=6.9441  webhooks > Retries and timeouts
       Your endpoint must respond within 10 seconds with a 2xx status code. If delivery fails, we retry with exponential backoff for up to 24 hours (8 attempts), then ...
  #2  score=4.9742  billing-invoices > Past-due accounts
       If payment fails after three retries, services are paused but your data is retained for 30 days. Update your payment method to resume immediately — no data is ...
  #3  score=4.7173  troubleshooting > Custom domain shows "Not secure"
       DNS is probably still propagating, which can take up to 48 hours. Verify your CNAME record points to `cname.acmecloud.example`. If it has been over 48 hours, check **Domains ...

=== HYBRID top-3 ===
  #1  score=0.0318  webhooks > Retries and timeouts
       Your endpoint must respond within 10 seconds with a 2xx status code. If delivery fails, we retry with exponential backoff for up to 24 hours (8 attempts), then ...
  #2  score=0.0315  webhooks > Supported events
       - `deploy.started` — a deployment began - `deploy.succeeded` — a deployment completed successfully - `deploy.failed` — a deployment failed (includes the build log excerpt) - `service.scaled` — autoscaling ...
  #3  score=0.0315  troubleshooting > Build failed: command exited with code 1
       The build command failed. Open the deploy log in the dashboard and look at the last 50 lines — the actual error is usually a missing dependency or ...

```
