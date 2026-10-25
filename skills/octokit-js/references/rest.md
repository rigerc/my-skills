# REST API, issues, pull requests and pagination

Use `octokit.rest` for readable, typed endpoint wrappers; use `octokit.request("METHOD /route", options)` when needing a newly exposed route. Both use Octokit's authentication, throttling and retry integration.

```js
const { data: repo } = await octokit.rest.repos.get({ owner, repo });
const { data: issue } = await octokit.rest.issues.get({ owner, repo, issue_number: 123 });
const { data: pull } = await octokit.rest.pulls.get({ owner, repo, pull_number: 123 });
```

## Safely listing everything

```js
const pages = octokit.paginate.iterator(octokit.rest.issues.listForRepo, {
  owner, repo, state: "open", per_page: 100,
});
let found = 0;
for await (const { data: items } of pages) {
  for (const item of items) {
    if (item.pull_request) continue; // REST issues collection includes PRs
    console.log(item.number, item.title);
    if (++found >= 50) break;
  }
  if (found >= 50) break;
}
```

`octokit.paginate(...)` assembles an array of all items; use it only when that is acceptable for memory and rate limits. Most endpoints default to a small page size (often 30). The maximum supported `per_page` often is 100 but varies by endpoint.

## Creating an issue (mutating)

```js
// Only run with the user's authorization and a token with required permission.
const { data } = await octokit.rest.issues.create({
  owner, repo, title, body,
});
console.log(data.html_url);
```

A PR can be created with `octokit.rest.pulls.create({ owner, repo, title, head, base, body })` when the necessary branches and permissions exist. Do not infer that `head` and `base` are interchangeable.

## Reading repository content

```js
const { data } = await octokit.rest.repos.getContent({
  owner, repo, path: "README.md",
  mediaType: { format: "raw" },
});
// A raw media response can be a string; typed return values vary by endpoint.
console.log(typeof data === "string" ? data : JSON.stringify(data));
```

`getContent` without raw media may return a file, directory list, or other object: narrow based on the `type` field before accessing `content`, and remember base64 encoded content where relevant.

## Error handling

```js
import { RequestError } from "octokit";
try {
  await octokit.rest.repos.get({ owner, repo });
} catch (error) {
  if (error instanceof RequestError) {
    console.error(`GitHub HTTP ${error.status}: ${error.message}`);
    // Check response headers / documentation for rate limiting or permissions.
  } else {
    throw error;
  }
}
```

See: https://github.com/octokit/octokit.js#rest-api

REST endpoint index: https://docs.github.com/en/rest
