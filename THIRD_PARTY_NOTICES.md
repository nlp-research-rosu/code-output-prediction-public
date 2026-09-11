# Third-party notices

Source identifiers, pinned revisions, and benchmark transformations are recorded
in each experiment's `problems/README.md` and `cases.json`. The table identifies
upstream material and the scope of the notices retained here; it does not grant
a new license to third-party material.

| Material | Pinned source | License record |
| --- | --- | --- |
| LiveCodeBench benchmark data | `livecodebench/code_generation_lite`, revision `25d8cb8f0db2efe1b589941eb8c26a219850d4d2` | The [pinned dataset card](https://huggingface.co/datasets/livecodebench/code_generation_lite/blob/25d8cb8f0db2efe1b589941eb8c26a219850d4d2/README.md) declares `cc` without specifying a Creative Commons license variant. |
| LiveCodeBench software notice | Copyright 2024 LiveCodeBench | The upstream software [MIT notice](LICENSES/LIVECODEBENCH-MIT.txt) is retained. It is not a blanket license for contest statements or selected solution programs. |
| DeepMind CodeContests | Revision `802411c3010cb00d1b05bad57ca77365a3c699d6` | [Creative Commons Attribution 4.0 International](https://creativecommons.org/licenses/by/4.0/), as recorded in the [source documentation](experiments/codecontests_reasoning_state_prediction/problems/README.md). |
| NetworkX `network_simplex` | Version 3.4.2, revision `2acf1590f82757c01a57b81b8c5dfb79e60aa416` | [BSD 3-Clause notice](experiments/networkx_network_simplex_state_prediction/problems/LICENSE-NETWORKX.txt). |
| AtCoder Library measurement headers | Version 1.6, revision `864245a00b00dd008d1abfdc239618fdb7d139da` | [CC0 notice](experiments/lcb_hard_v1_cpp/measurements/program-complexity/support/ATCODER-LICENSE); used as compilation dependencies outside measured source scope. |

The selected LiveCodeBench programs retain their contest identifiers. The
pinned dataset card does not establish authorship or licensing of the selected
solution-source bytes. Source attribution and applicable terms remain specific
to those programs.

The selected CodeContests programs retain their source metadata and attribution.
For this benchmark, legal inputs were selected and deterministic checkpoint
instrumentation was added. These modifications are identified in the experiment
manifests and are not endorsed by the original dataset authors.

Classic Algorithms programs are repository-authored implementations; their
literature references identify the algorithms, not copied source code. No new
blanket license for repository-authored material is asserted by this notice.
