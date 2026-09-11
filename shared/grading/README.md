# Grading outcomes

Every gradable model response is classified along two independent axes:

1. **Correctness:** whether an unambiguous answer matches the committed oracle.
2. **Validity:** whether the complete assistant response is exactly one JSON
   object with one string field, `{"output": "<answer>"}`.

This produces four outcome statuses:

| Status | Answer matches oracle | Response envelope valid | Accuracy treatment |
| --- | --- | --- | --- |
| `correct_valid` | yes | yes | correct and eligible |
| `correct_invalid` | yes | no | correct and eligible |
| `wrong_valid` | no | yes | wrong and eligible |
| `wrong_invalid` | no | no | wrong and eligible |

`valid` describes only the outer response envelope. It does not mean the answer
inside `output` is correct or, when a task expects JSON output, valid JSON.
Likewise, `invalid` does not automatically mean the answer is wrong.

For an invalid envelope, the shared grader checks only conservative,
unambiguous candidates: the complete response, the complete body of one
Markdown JSON fence, and a decodable embedded object whose only field is a
string-valued `output`. It never repairs truncated JSON, changes quotes, or
guesses the intended answer. A matching candidate is `correct_invalid`;
otherwise the outcome is `wrong_invalid`.

Accuracy is calculated as:

```text
(correct_valid + correct_invalid)
---------------------------------
all four correct/wrong statuses
```

`no_response`, `transport_error`, `not_run`, and other explicitly ungraded
states remain separate and are excluded from both the numerator and denominator.
The workbench parser's `parsed_output` and `invalid_format` values describe the
response-parsing stage; graders convert those states into the four outcome
statuses above.

## Study-specific answer comparison

The exact-output task is graded with the original study's comparison rule.
Rows below identify the studies; the comparison describes how a candidate
answer is checked against the committed oracle. These rules apply equally to
valid and conservatively recovered invalid response envelopes.

| Study | Answer comparison |
| --- | --- |
| Classic Algorithms and both LiveCodeBench studies | Parsed JSON equality when the oracle is JSON; otherwise whitespace-separated token equality |
| CodeContests | Ordered signed-integer and alphabetic-token sequences; separator punctuation is ignored |
| NetworkX network simplex | Byte-for-byte equality |

These policies reproduce 4,361 correct predictions among 11,151 gradable
responses. The remaining 49 selected prediction cells have no response and are excluded
from accuracy. Comparisons across studies should account for these different
normalization rules.
