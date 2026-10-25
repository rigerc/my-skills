# GitHub Apps, installations, signed webhooks and OAuth

## Installation client

```js
import { readFile } from "node:fs/promises";
import { App } from "octokit";
const privateKey = await readFile(process.env.GITHUB_APP_PRIVATE_KEY_FILE, "utf8");
const app = new App({
  appId: Number(process.env.GITHUB_APP_ID),
  privateKey,
});
const octokit = await app.getInstallationOctokit(Number(process.env.GITHUB_INSTALLATION_ID));
const { data } = await octokit.rest.repos.get({ owner, repo });
console.log(data.full_name);
```

For GitHub App operations, grant the minimal declared permissions and install the App on the target repositories. For multi-installation automation, `app.eachRepository.iterator()` yields scoped clients and repositories; consider separate rate budgets.

## Verified webhook delivery

Use `createNodeMiddleware(app)`, which implements verification before processing. Register event handlers on `app.webhooks`:

```js
import { createServer } from "node:http";
import { App, createNodeMiddleware } from "octokit";
const app = new App({ appId, privateKey, webhooks: { secret: webhookSecret } });
app.webhooks.on("issues.opened", async ({ payload }) => {
  console.log(payload.repository.full_name, payload.issue.number);
});
createServer(createNodeMiddleware(app)).listen(3000);
// POST /api/github/webhooks
```

Never run handlers against unverified JSON received directly from the internet. Verify signatures even in serverless environments (use `app.webhooks.verifyAndReceive`). Make handlers idempotent when GitHub retries delivery. Limit webhook body sizes and apply server/runtime security hardening in production. The illustration above is not a hardened production service.

## OAuth

For GitHub user sign-in, `App` provides OAuth methods for GitHub Apps; `OAuthApp` supports OAuth Apps. Keep client secrets and token exchange on the server, validate `state`, and follow appropriate refresh and token-rotation procedures. Never embed App credentials in public browser bundles.

Upstream: https://github.com/octokit/octokit.js#app-client

GitHub Apps docs: https://docs.github.com/en/apps

Webhook docs: https://docs.github.com/en/webhooks
