# Program source and arm construction

The programs come from the validation and test splits of
`deepmind/code_contests` at revision
`802411c3010cb00d1b05bad57ca77365a3c699d6`, licensed CC-BY-4.0.
Selection was fixed before model outcomes were inspected.

The candidate pool contained 282 programs rated 2400--3500. Seventy-nine met
the initial C++, public-input, standard-I/O, noninteractive, and cohort rules.
Sixty-six supported deterministic candidate inputs and a checkpoint. Twenty-
five also had an input-sensitive selected loop. Twenty-four supported a
candidate shared state projection inside and immediately after that loop;
repeated cross-runtime validation retained twenty-two.

Codeforces 1603F had no deterministic post-loop checkpoint. Codeforces 1622F
used a time-seeded random hash and produced different post-loop state oracles.
Codeforces 1619H exposed `rand()`-dependent treap state whose oracle differed
between the construction and locked measurement runtimes. No program was
dropped because of model accuracy. The search was not exhaustive over all
CodeContests programs.

For each selected program:

- `short-trace-final` uses a public legal input and requests final output;
- `long-trace-final` uses the same clean source with a measured longer trace;
- `inside-loop-state` stops at a deterministic selected-loop entry and prints
  canonical JSON for the declared core state;
- `post-loop-state` lets that loop finish, then prints the same ordered fields
  and types before any unrelated state change.

The CodeContests construction targets a checkpoint near the 100th entry into
the selected loop. For each case, it uses a nearby entry where the inside and
post-loop checkpoints expose a deterministic state change with matching fields
and types. The retained checkpoints range from 80 to 114. This is lower than
the default used for LiveCodeBench because the two corpora used different
construction targets, not because one corpus is assumed to be harder.

The clean-source arms preserve the selected solution bytes. Instrumented arms
add only checkpoint observation and early exit. The exact source, input, and
hidden oracle used for each prediction are committed below this directory.
`cases.json` records source hashes, input hashes, selected-loop anchors,
projection fields, checkpoint hashes, and validation flags.
