# Full-Stack AI Engineer (Claude Skill)

A Claude skill that makes Claude work like a principal-level full-stack AI engineer: it picks the right depth of process, loads only the references a task needs, runs an inspect-implement-test-verify loop, and reports honestly on what was and was not checked.

Covers LLM apps, RAG, agents and MCP, multimodal and voice AI, Next.js frontends, backends, data, security, testing and evals, deployment, and cost. Includes runnable helper scripts for evals and project validation.

## Install

Choose the surface you use. Skills do not sync between surfaces, so install on each one separately.

### Claude.ai (web, desktop, mobile)
Requires a Pro, Max, Team, or Enterprise plan with code execution enabled (Enterprise owners must enable Skills in Admin settings first).

1. Download `full-stack-ai-engineer.zip` from this repo's **Releases** page (or build it with `./build-zip.sh`).
2. Open **Settings > Capabilities > Skills**.
3. Click **Upload skill** and select the ZIP.
4. Toggle the skill on.

The ZIP must contain a folder named exactly `full-stack-ai-engineer` with `SKILL.md` inside it.

### Claude Code: as a skill folder
```bash
git clone https://github.com/yousafaiofficial/full-stack-ai-engineer-skill.git
# personal (all projects)
cp -r full-stack-ai-engineer-skill/plugins/full-stack-ai-engineer/skills/full-stack-ai-engineer ~/.claude/skills/
# or project-only
mkdir -p .claude/skills && cp -r full-stack-ai-engineer-skill/plugins/full-stack-ai-engineer/skills/full-stack-ai-engineer .claude/skills/
```

### Claude Code: as a plugin (installs and updates from GitHub)
```bash
claude plugin marketplace add yousafaiofficial/full-stack-ai-engineer-skill
claude plugin install full-stack-ai-engineer@fsai-skills
```
Inside a session you can also use `/plugin marketplace add yousafaiofficial/full-stack-ai-engineer-skill`. A plugin skill is namespaced by the plugin name.

## Repo layout

```
.claude-plugin/marketplace.json                          marketplace catalog (Claude Code)
plugins/full-stack-ai-engineer/
  .claude-plugin/plugin.json                             plugin manifest
  skills/full-stack-ai-engineer/                         the skill itself
    SKILL.md  README.md  CHANGELOG.md
    references/  templates/  scripts/
build-zip.sh                                             builds the claude.ai upload ZIP
LICENSE  .gitignore
```

See `plugins/full-stack-ai-engineer/skills/full-stack-ai-engineer/README.md` for how the skill works, example prompts, and customization.

## Releasing a new version
1. Edit the skill, then update `CHANGELOG.md` and the version in `plugin.json` (and the skill README).
2. `claude plugin validate .` and `./build-zip.sh`.
3. Commit, tag (`git tag v3.1.0 && git push --tags`), and attach `dist/full-stack-ai-engineer.zip` to a GitHub Release.

## Author
Built and maintained by Muhammad Yousaf ([@yousafaiofficial](https://github.com/yousafaiofficial)).

## License
MIT. See `LICENSE`.
