// Read public repository details (a token is optional for public repositories).
import { Octokit } from "octokit";

const token = process.env.GITHUB_TOKEN ?? process.env.GH_TOKEN;
const octokit = new Octokit(token ? { auth: token } : {});

const { data } = await octokit.rest.repos.get({
  owner: "octokit",
  repo: "octokit.js",
});
console.log(data.full_name, data.html_url);
