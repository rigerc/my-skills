# Troubleshooting and source links

| Symptom | Likely cause / next step |
|---|---|
| `ERR_REQUIRE_ESM` or cannot use import | Use native ESM (`.mjs` or `"type":"module"`); do not use CommonJS `require("octokit")` examples with modern releases. |
| Fetch is missing | Use supported Node.js (Octokit v5 package requires Node >=20) or check fetch compatibility in the installed package. |
| `401 Bad credentials` | Confirm the credential exists, is not expired/revoked, and is provided via `auth`; never print it. |
| `403 Resource not accessible by integration` | Check fine-grained token permissions, App installation scope, Actions workflow `permissions`, organization policies. |
| `404 Not Found` on private repo | Could be wrong owner/name or intentionally hidden authorization failure. |
| Secondary rate limit / abuse protection | Reduce concurrency, obey retry recommendations, batch only where appropriate, avoid aggressively retrying writes. Octokit bundles retry/throttling features. |
| PRs show up in issue listing | Filter out entries with `pull_request`, or use `octokit.rest.pulls.list`. |
| Webhook event not handled | Verify webhook URL, delivery signature/secret, event subscriptions and permissions; inspect GitHub webhook deliveries. |
| GraphQL pagination repeats results | Supply `after: $cursor`, read `endCursor`, and request proper `pageInfo`. |
| GitHub Enterprise Server requests fail | Set correct REST `baseUrl` (usually `/api/v3`); verify compatibility and authorization. |

## Verified upstream documentation (2026-10-23)

- Octokit monorepo and SDK README: https://github.com/octokit/octokit.js
- Official GitHub Octokit scripting guide: https://docs.github.com/en/rest/guides/scripting-with-the-rest-api-and-javascript
- GitHub REST reference: https://docs.github.com/en/rest
- GitHub GraphQL reference: https://docs.github.com/en/graphql
- GitHub Apps: https://docs.github.com/en/apps
- Agent Skills format: https://agentskills.io/specification

Always verify a method name and required permissions against the current endpoint-specific documentation before shipping production changes. This skill provides examples, not a frozen API specification.
