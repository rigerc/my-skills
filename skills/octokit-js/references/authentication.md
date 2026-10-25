# Authentication and permissions

## Which credential to use

| Environment | Recommended approach | Notes |
|---|---|---|
| Personal CLI/local automation | Fine-grained personal access token (PAT) | Choose only required repositories and REST permissions; set `GITHUB_TOKEN` in environment or secret manager. |
| GitHub Actions | Workflow-supplied `GITHUB_TOKEN` | Use minimal `permissions:`; default token is scoped primarily to its workflow repository. |
| Installed GitHub App | `App` and `getInstallationOctokit(installationId)` | App JWT and installation token are handled by SDK. Install the App on the relevant repositories and grant required permissions. |
| OAuth user login | GitHub App OAuth or `OAuthApp` | Keep client secrets on a backend and protect authorization flow with `state`. |
| Public reads | No token, if allowed | More stringent rate limits and no access to private resources. |

## Standard client

```js
import { Octokit } from "octokit";
const token = process.env.GITHUB_TOKEN ?? process.env.GH_TOKEN;
const octokit = new Octokit({
  ...(token ? { auth: token } : {}),
  userAgent: "my-integration/1.0",
  ...(process.env.GITHUB_API_URL ? { baseUrl: process.env.GITHUB_API_URL } : {}),
});
```

If a specific operation requires authentication, fail before making the request when no token is set. Do not log token-bearing HTTP request headers.

## GitHub Actions

Use a minimally permissioned workflow, e.g.:

```yaml
permissions:
  contents: read
  issues: read
```

Set `GITHUB_TOKEN` from GitHub's workflow-provided secret in the consuming workflow environment. For writing issues, replace `issues: read` with `issues: write` and obtain authorization before committing such a workflow. Fork pull-request workflows can have further restrictions. App installations are a better option for cross-repository operations when `GITHUB_TOKEN` is insufficient.

## Permissions and common failures

- Fine-grained PATs often require **Issues: Read/Write** for issue operations, **Pull requests: Read/Write** for PR operations, and **Contents: Read/Write** for file operations. Endpoint permissions vary; consult each GitHub REST endpoint's "Fine-grained access tokens" section.
- GitHub App authentication involves both declared App permissions and **installation scope** (selected organizations/repositories).
- `401` usually indicates absent/invalid credentials. `403` may indicate denied permissions, rate limits, SSO or organization policy. `404` can deliberately mask inaccessible private repositories. Check endpoint docs and response headers.
- `GITHUB_API_URL` should be the REST API root, e.g. `https://github.example.com/api/v3` on GitHub Enterprise Server. GraphQL support/configuration can vary by server version.

Docs: https://docs.github.com/en/rest/authentication/authenticating-to-the-rest-api

Docs: https://docs.github.com/en/actions/security-for-github-actions/security-guides/automatic-token-authentication
