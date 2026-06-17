🧵 How I use Claude Code to read codebases I didn't write — a thread:

1/ You get handed a codebase. Thousands of files, no one around to explain them. Most devs cope by grep-ing around and hoping for the best. There's a better way.

2/ The core insight: reading code involves two kinds of questions. Structural (what calls what?) and meaning (why does this exist?). Claude Code handles the structural ones so you can focus on meaning.

3/ Start with a map, not a file. Ask for a structural overview — main modules, entry points, and the most central files. This single prompt gives you orientation that would take hours of browsing.

4/ Trace paths, not files. Pick a real flow — like "login form submit to session cookie" — and follow it end to end. Three or four traced paths and you understand most of the codebase.

5/ Use Plan Mode (Shift+Tab) for zero-side-effect exploration. Ask ambitious questions, validate your mental model, iterate on understanding — without touching any files.

6/ Git history is underrated documentation. Ask Claude to summarize the history of a confusing file. The commit that introduced weird code usually explains why it's weird.

7/ Build a CLAUDE.md as you go — encode entry points, key paths, conventions, and gotchas. Exploration isn't wasted work if you capture what you learn. Full post: selamy.dev/reading-code-you-didnt-write
