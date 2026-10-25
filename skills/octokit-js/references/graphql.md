# GitHub GraphQL with Octokit

Use `octokit.graphql(query, variables)` for relationships that would otherwise require many REST round trips. Bind user input as variables, never interpolate untrusted text into the query source.

```js
const response = await octokit.graphql(`
  query ($owner: String!, $repo: String!, $first: Int!) {
    repository(owner: $owner, name: $repo) {
      nameWithOwner
      issues(first: $first, states: OPEN) {
        nodes { number title url }
        pageInfo { hasNextPage endCursor }
      }
    }
  }
`, { owner, repo, first: 20 });
console.log(response.repository.issues.nodes);
```

## Cursor pagination

GraphQL connections typically cap page size at 100. To page, request `pageInfo { hasNextPage endCursor }` and pass `after: $cursor` to a connection. Octokit also supports `octokit.graphql.paginate(...)` when the expected connection and `pageInfo` structure are present. Example:

```js
const result = await octokit.graphql.paginate(`
  query ($owner: String!, $repo: String!, $cursor: String) {
    repository(owner: $owner, name: $repo) {
      issues(first: 100, after: $cursor) {
        nodes { number title }
        pageInfo { hasNextPage endCursor }
      }
    }
  }
`, { owner, repo });
```

GraphQL errors can include field-specific permission failures or rate/cost limits. Select only required fields. If you're seeking all results from very large repositories, bound work and use cursor checkpoints.

Example script: `examples/graphql-issues.mjs`.

Docs: https://docs.github.com/en/graphql

Upstream: https://github.com/octokit/octokit.js#graphql-api-queries
