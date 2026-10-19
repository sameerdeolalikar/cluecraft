# Cluecraft roadmap

This is a new project with an initial CLI, not an established puzzle platform.
The following estimates describe planned work, not completed sessions or a claim
of existing users. Priorities should follow actual puzzle construction and play.

| Work | Acceptance criteria | Estimate |
| --- | --- | --- |
| Interactive puzzle constructor | Draw/erase cells, resize, undo, import/export text and clue JSON; keyboard access | 9–13 hours |
| Explainable logical hints | Implement overlap and forced-empty deductions; show a reason for each change; avoid claiming a guess is a logical deduction | 8–12 hours |
| Faster constraint propagation | Filter row/column domains before branching; preserve unknown status at resource limits; compare with exhaustive small cases | 5–8 hours |
| Printable puzzle booklets | Multiple puzzles, separate answer pages, A4/Letter layout, original titles, PDF export | 6–9 hours |
| Puzzle quality checks | Flag ambiguous designs, compare changed clues, distinguish solver effort from human difficulty | 4–6 hours |
| Packaging and usability | Cross-version CI, example gallery, physical print checks, error-message and accessibility review | 3–5 hours |

**Estimated remaining work: 35–53 hours.** Examples should remain original,
synthetic puzzle designs. No AI model development or evaluation, scraped puzzle
collections, or personal-data processing is planned.
