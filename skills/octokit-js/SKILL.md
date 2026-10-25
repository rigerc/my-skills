---
name: octokit-js
description: Help build, review, and debug JavaScript or TypeScript integrations with GitHub using Octokit.js. Use for GitHub REST and GraphQL requests, pagination, authentication, GitHub Apps, webhook verification, permissions, and safe issue or pull-request automation.
license: MIT
compatibility: Node.js 20+ for current Octokit releases; the consuming project must provide the octokit dependency for the JavaScript examples.
metadata:
  version: "1.1.0"
  source: "https://github.com/octokit/octokit.js"
---

# Octokit.js

Use the official [Octokit.js](https://github.com/octokit/octokit.js) SDK when working with the GitHub API in JavaScript or TypeScript. Favor modern ESM imports:

```js
import { Octokit } from "octokit";
```

This skill contains **guidance and small examples only**. It does not include a `package.json`, lockfile, project scaffolding, executable CLI, vendored library, or credentials. The examples assume `octokit` is already installed in the consuming project; follow that project's dependency-management process rather than installing packages inside this skill folder.

## Workflow

1. Confirm the task, target GitHub repository, runtime (Node.js, Actions, browser, or GitHub Enterprise Server), and whether the task is read-only or changes remote state.
2. Select the least-privileged authentication method: a fine-grained personal access token for personal integrations; the workflow-provided `GITHUB_TOKEN` for Actions; or an installation client for GitHub Apps. Some public REST reads need no token.
3. For REST, prefer `octokit.rest.<area>.<operation>(params)`. Use `octokit.request("METHOD /route", params)` where needed. For GraphQL, use `octokit.graphql(query, variables)` with variables rather than interpolated user input.
4. Handle pagination, API errors, permissions, and rate limits. For long REST result sets, prefer `octokit.paginate.iterator(...)` to collecting every result in memory. GraphQL connections need `pageInfo` and cursor-based requests.
5. Before performing GitHub mutations (for example, creating issues, posting comments, or merging PRs), confirm the intended target and required authorization. Do not treat examples as authorization to make live changes.
6. Verify operation names and required permissions in current GitHub documentation before relying on the code in production.

## Basic client

```js
import { Octokit } from "octokit";

const token = process.env.GITHUB_TOKEN ?? process.env.GH_TOKEN;
const octokit = new Octokit({
  ...(token ? { auth: token } : {}),
  ...(process.env.GITHUB_API_URL ? { baseUrl: process.env.GITHUB_API_URL } : {}),
});
```

Never hard-code, print, or commit tokens or private keys. Keep credentials out of browser bundles. For GitHub Enterprise Server, confirm the correct API base URL (often ending in `/api/v3`).

## REST

```js
const { data: repo } = await octokit.rest.repos.get({
  owner: "octokit",
  repo: "octokit.js",
});
console.log(repo.full_name);
```

When listing issues via the REST API, entries representing pull requests can also appear. Filter out entries with a `pull_request` property when only issues are wanted. A `401` commonly indicates an invalid credential; `403` can indicate permissions, organization policy, or a rate limit; a private repository may return `404` without appropriate access.

## GraphQL

```js
const result = await octokit.graphql(`
  query ($owner: String!, $repo: String!) {
    repository(owner: $owner, name: $repo) {
      nameWithOwner
    }
  }
`, { owner: "octokit", repo: "octokit.js" });
console.log(result.repository?.nameWithOwner);
```

Always bind input as GraphQL variables. Paginate connections with `pageInfo { hasNextPage endCursor }` and an `after` cursor.

## GitHub Actions, Apps, and webhooks

In Actions, pass the workflow-provided `GITHUB_TOKEN` and set narrowly scoped permissions, for example:

```yaml
permissions:
  contents: read
  issues: read
```

For GitHub Apps, use `App` from `octokit` and an installation-specific client (`app.getInstallationOctokit(installationId)`). App permissions **and** repository installation access must allow the operation. Verify webhook signatures through Octokit's webhook handling before trusting or acting on payloads; never parse unauthenticated webhook data as verified events.

## Small examples

- [`examples/repository-read.mjs`](examples/repository-read.mjs) — retrieve repository information with REST.
- [`examples/list-issues.mjs`](examples/list-issues.mjs) — read and filter open issues.
- [`examples/graphql-issues.mjs`](examples/graphql-issues.mjs) — request issues with GraphQL variables.

These examples are **read-only** and make API calls only when explicitly run in a project with its dependency installed. Edit `owner` and `repo` to match the intended target. For private repositories and GraphQL, provide `GITHUB_TOKEN` or `GH_TOKEN` through your runtime's secret management.

## Official references

- [Octokit.js](https://github.com/octokit/octokit.js)
- [GitHub REST API](https://docs.github.com/en/rest)
- [GitHub GraphQL API](https://docs.github.com/en/graphql)
- [GitHub Apps](https://docs.github.com/en/apps)
- [GitHub Actions token authentication](https://docs.github.com/en/actions/security-for-github-actions/security-guides/automatic-token-authentication)
