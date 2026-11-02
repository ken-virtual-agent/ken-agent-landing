# HireAI deployment

HireAI is a static page with a Netlify Function proxy for Luna's chat. Deploy
the repository to Netlify using the included `netlify.toml`; the site publish
directory is the repository root.

Set the `LUNA_WEBHOOK_URL` environment variable in Netlify to the active n8n
webhook URL. The default in the function is the supplied n8n test webhook;
`webhook-test` URLs only work while the workflow is listening for a test event.

The function is available at `/.netlify/functions/ask-luna`. To make it work
on `https://kenagent.xyz/hireai/`, configure `kenagent.xyz` as a custom domain
for the Netlify site and point its DNS to Netlify. The domain currently serves
from GitHub Pages, which cannot run Netlify Functions.
