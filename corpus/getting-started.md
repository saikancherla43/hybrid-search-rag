# Getting Started with Acme Cloud

Welcome to Acme Cloud, the deployment platform for modern teams. This guide walks you through creating your first project.

## Create an account

Sign up at app.acmecloud.example with your work email. You can start on the free Starter plan — no credit card required. After confirming your email, you will land in the Acme Cloud dashboard.

## Create your first project

Click **New Project** in the dashboard. Give the project a name and choose a region: `us-east`, `us-west`, or `eu-central`. Acme Cloud deploys your services in the selected region for low latency. Most customers pick the region closest to their users.

## Connect a repository

Acme Cloud integrates with GitHub, GitLab, and Bitbucket. Authorize the Acme Cloud app, then select the repository you want to deploy. On every push to your main branch, Acme Cloud automatically builds and deploys your code.

## Deploy your first service

During project creation, choose a service type: **Web Service**, **Worker**, or **Cron Job**. For a typical web app, pick Web Service and set the build command (e.g. `npm run build`) and start command (e.g. `npm start`). Your first deploy usually completes in under five minutes.

## Invite your team

Go to **Settings → Team** to invite teammates by email. Starter plans include 3 seats; Growth plans include 25 seats and Scale plans are unlimited.

## Next steps

Once your first service is live, explore environment variables, custom domains, and autoscaling in the docs. If you get stuck, our support team responds within 4 business hours on paid plans.
