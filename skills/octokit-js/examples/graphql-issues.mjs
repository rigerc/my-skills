// Read the first 10 open issues with GraphQL variables.
import { Octokit } from "octokit";

const token = process.env.GITHUB_TOKEN ?? process.env.GH_TOKEN;
if (!token) throw new Error("Set GITHUB_TOKEN or GH_TOKEN for GraphQL access");
const octokit = new Octokit({ auth: token });

const { repository } = await octokit.graphql(`
  query ($owner: String!, $repo: String!) {
    repository(owner: $owner, name: $repo) {
      issues(first: 10, states: OPEN) {
        nodes { number title }
      }
    }
  }
`, { owner: "octokit", repo: "octokit.js" });

for (const issue of repository.issues.nodes) {
  console.log(`#${issue.number}: ${issue.title}`);
}
