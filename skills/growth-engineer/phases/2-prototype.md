# Phase 2 — Prototype

Goal: the user sees every option on their real UI, looking finished, before anything exists in Levered. Design decisions get made here: once the optimization is live, its design can't be reshaped.

## 1. Build it

Follow [../references/prototype.md](../references/prototype.md) (SDK) or the preview section of [../references/integration-web-tag.md](../references/integration-web-tag.md) (web tag). For the SDK:

- **Make the permissions last** before the first command, unless the session runs in auto mode ([../references/permissions.md](../references/permissions.md)).
- **Work on a branch.** Before the first edit, `git checkout -b levered/<surface>`, and say so in one line. Their main code stays untouched, which is why one "build them" covers every edit that follows.
- **Start installs in the background the moment they say yes**, with the project's own installer and bare commands: the dependencies if `node_modules` is missing (check with a plain `ls node_modules`), then the SDK (`@levered_dev/sdk`), and, only if this session has no browser tool of its own, the screenshot browser (`npx playwright install chromium` from the project root). Write the code while they install, using the imports exactly as the reference gives them.
- **Then run the project's type check or build**, and dig into the SDK only if that fails. To tell whether a failing test was already failing, commit your work on the branch, check out the base branch, run the tests, and switch back — never `git stash`. Any change to project-wide config (TypeScript, build, middleware, auth, launch config) is said in a line and listed in the summary.
- **Start the dev server yourself**, in the background, and remember the optimized page's URL so nobody is asked for it again.

## 2. Make each option look finished

An option is the whole presentation of an idea, not a swapped element: adjust whatever the change affects so it reads as designed, in the site's own design language. Touch nothing outside the option's purpose, so the baseline stays today's page.

## 3. Review your own work, then guide theirs

**Look at every version** — with your own browser tool if this session has one (each version's `?levered_variant=` link), otherwise with screenshots — as a designer would, and fix whatever would make it look unfinished or bolted on.

**Then open the real page for the user** — the surface on the dev server, where the Levered pill switches between the versions: `open http://localhost:<port>/<path>` (macOS; elsewhere give the URL). Walk them through it, starting with the version that matters most, then ask with a card:

> It's open at <the URL>; the Levered pill <where it is> switches between the <n> versions. Start with <the bet>, that's the bet. <One or two tweaks you'd still make, and why.> <The question only they can answer>?
>
> **[<Apply the tweaks> and continue (Recommended)] [<a narrower alternative>] [<another path>]**

**A tweak is part of this design now, or an idea for later.** Fold it in now if it's worth doing; otherwise note it as an idea for `.levered/`. A live optimization can't take new changes yet, so nothing gets planned for after launch.

## 4. Iterate, then wait for an explicit go

Each pass: edit, look again, show what changed, and re-check the version count against traffic when options change. Move on only on an explicit go to wire it up: agreeing with one version is a reaction, not approval to create anything in Levered.
