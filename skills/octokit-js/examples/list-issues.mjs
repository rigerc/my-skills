// List open issues; GitHub's REST issue endpoint also returns pull requests.
import { Octokit } from "octokit";

const token = process.env.GITHUB_TOKEN ?? process.env.GH_TOKEN;
const octokit = new Octokit(token ? { auth: token } : {});

const { data } = await octokit.rest.issues.listForRepo({
  owner: "octokit",
  repo: "octokit.js",
  state: "open",
  per_page: 20,
});

for (const issue of data.filter((item) => !item.pull_request)) {
  console.log(`#${issue.number}: ${issue.title}`);
}
