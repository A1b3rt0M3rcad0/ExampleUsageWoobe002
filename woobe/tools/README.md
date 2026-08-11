# Atlas HTTP Tools

HTTP is the correct MVP integration for Atlas. Atlas already exposes a small REST contract, so adding an MCP server would add protocol/runtime surface without adding product value.

Create a Woobe Secret named `ATLAS_HTTP_AUTHORIZATION` whose secret value is:

`Bearer <ATLAS_WOOBE_TOOL_TOKEN>`

Woobe's HTTP Tool secret resolver replaces a header value that uses `{{secret:SECRET_NAME}}` with the decrypted secret. For that reason the `Bearer ` prefix belongs inside the secret value.

Then create:
- `Atlas Assessment Context` from `atlas-assessment-context.json`
- `Atlas Evidence API` from `atlas-evidence-api.json`

Replace the example base URL before saving.

Bindings:
- Risk Coordinator: Atlas Assessment Context
- Security Analyst: Atlas Assessment Context + Atlas Evidence API
- Legal Analyst: Atlas Assessment Context + Atlas Evidence API
- Compliance Analyst: Atlas Assessment Context + Atlas Evidence API

All routes use `default_permission=allow` and LOW risk because they are assessment-scoped reads. There are intentionally no write-capable Tools in the PoV.
