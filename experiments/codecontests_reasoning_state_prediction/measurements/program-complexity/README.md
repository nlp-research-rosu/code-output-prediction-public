# Complexity measurements

This experiment retains the repository's four separate complexity dimensions. Metric names, formulas, units, and interpretation are defined in the [shared metric definitions](../../../../shared/metrics/README.md).

## Omega_CC

| Program | Original | Inside-loop | Post-loop |
| --- | ---: | ---: | ---: |
| 1580F | 42 | 50 | 50 |
| 1615G | 84 | 92 | 92 |
| 1599D | 86 | 94 | 94 |
| 1603E | 24 | 32 | 32 |
| 1608F | 25 | 33 | 33 |
| 1615H | 37 | 45 | 45 |
| 1552G | 18 | 26 | 26 |
| 1569F | 60 | 68 | 68 |
| 1572E | 28 | 36 | 36 |
| 1553H | 23 | 31 | 31 |
| 1608E | 76 | 84 | 84 |
| 1572D | 37 | 47 | 47 |
| 1617E | 128 | 136 | 136 |
| 1567F | 42 | 50 | 50 |
| 1574F | 86 | 96 | 96 |
| 1580B | 21 | 29 | 29 |
| 1599J | 55 | 63 | 63 |
| 1569E | 47 | 55 | 55 |
| 1586F | 13 | 21 | 21 |
| 1556F | 69 | 79 | 79 |
| 1598F | 13 | 21 | 21 |
| 1620G | 19 | 27 | 27 |

## Omega_hat_NativeTrace

| Program | Short-trace final | Long-trace final | Inside-loop state | Post-loop state |
| --- | ---: | ---: | ---: | ---: |
| 1580F | 58,249,376 | 58,258,370 | 58,233,084 | 58,233,011 |
| 1615G | 194 | 5,325 | 6,517 | 6,693 |
| 1599D | 101,190 | 105,223 | 104,008 | 103,972 |
| 1603E | 2,469 | 20,737,394 | 3,687,795 | 4,331,747 |
| 1608F | 1,337 | 607,758 | 36,748 | 36,955 |
| 1615H | 5,714 | 15,049 | 8,943 | 8,891 |
| 1552G | 473 | 2,634 | 464 | 378 |
| 1569F | 9,950 | 150,522 | 118,714 | 118,625 |
| 1572E | 17,610 | 94,129 | 1,931 | 1,903 |
| 1553H | 371 | 2,577 | 1,846 | 1,815 |
| 1608E | 3,627 | 17,917 | 7,468 | 7,931 |
| 1572D | 888 | 1,887 | 1,793 | 1,703 |
| 1617E | 2,124 | 50,271 | 3,086 | 3,349 |
| 1567F | 2,028 | 7,387 | 3,975 | 3,936 |
| 1574F | 1,209 | 1,513,963,426 | 8,102,841 | 16,200,040 |
| 1580B | 2,095 | 164,275,450 | 839 | 753 |
| 1599J | 341 | 45,221 | 4,562 | 4,930 |
| 1569E | 963 | 9,765,064 | 14,587 | 4,686,010 |
| 1586F | 110 | 41,386 | 2,866 | 2,768 |
| 1556F | 475 | 17,617,324 | 202,474 | 17,086,448 |
| 1598F | 59 | 112,813 | 1,491 | 1,432 |
| 1620G | 1,031 | 32,711 | 6,489 | 6,476 |

## Omega_hat_StateSize

| Program | Short-trace final | Long-trace final | Inside-loop state | Post-loop state |
| --- | ---: | ---: | ---: | ---: |
| 1580F | 840,185 | 840,619 | 840,524 | 840,524 |
| 1615G | 70 | 1,108 | 1,108 | 1,108 |
| 1599D | 4,002,117 | 4,002,178 | 4,002,178 | 4,002,178 |
| 1603E | 1,478,716 | 1,478,716 | 1,478,716 | 1,478,716 |
| 1608F | 457,776 | 457,776 | 463,089 | 463,088 |
| 1615H | 32,724 | 32,835 | 32,763 | 32,763 |
| 1552G | 239 | 202 | 205 | 204 |
| 1569F | 8,692,110 | 8,692,304 | 8,692,014 | 8,692,013 |
| 1572E | 126,917 | 126,917 | 126,917 | 126,917 |
| 1553H | 42 | 213 | 212 | 213 |
| 1608E | 25,200,111 | 25,200,169 | 25,200,162 | 25,200,162 |
| 1572D | 9,937,295 | 9,937,295 | 9,937,306 | 9,937,306 |
| 1617E | 200,424 | 201,774 | 200,204 | 200,231 |
| 1567F | 2,041,765 | 2,041,833 | 2,041,801 | 2,041,801 |
| 1574F | 163 | 11,912,938 | 2,100,036 | 2,100,035 |
| 1580B | 1,082,351 | 1,082,455 | 1,082,353 | 1,082,352 |
| 1599J | 70 | 930 | 479 | 522 |
| 1569E | 2,796 | 395,926 | 3,310 | 199,318 |
| 1586F | 1,011,054 | 1,011,696 | 1,011,696 | 1,011,696 |
| 1556F | 33 | 2,289 | 3,313 | 3,312 |
| 1598F | 20 | 1,483 | 1,199 | 1,199 |
| 1620G | 8,389,238 | 8,389,243 | 8,389,243 | 8,389,243 |

## Omega_hat_StateLoad

| Program | Short-trace final | Long-trace final | Inside-loop state | Post-loop state |
| --- | ---: | ---: | ---: | ---: |
| 1580F | 41,166,621,651,798 | 41,173,337,298,488 | 41,157,227,775,110 | 41,157,233,657,412 |
| 1615G | 6,874 | 2,793,543 | 6,401,288 | 6,582,454 |
| 1599D | 2,823,867,851 | 12,567,049,367 | 11,758,615,723 | 11,898,690,449 |
| 1603E | 909,408,818 | 4,501,797,683,908 | 189,201,355,791 | 194,205,315,507 |
| 1608F | 151,484,570 | 54,207,437,289 | 20,733,502,691 | 20,758,637,829 |
| 1615H | 168,597,991 | 316,956,724 | 204,519,776 | 205,469,759 |
| 1552G | 95,040 | 351,855 | 54,746 | 56,528 |
| 1569F | 30,961,555,303,243 | 31,005,550,097,240 | 30,965,699,084,189 | 30,965,722,726,988 |
| 1572E | 2,943,713,730 | 17,161,896,034 | 268,420,712 | 284,284,662 |
| 1553H | 7,814 | 288,995 | 270,178 | 275,715 |
| 1608E | 62,438,640,242 | 405,236,280,252 | 175,461,364,750 | 189,044,239,492 |
| 1572D | 4,040,733,206 | 9,933,542,529 | 10,817,965,812 | 10,976,962,293 |
| 1617E | 208,350,789 | 4,912,863,519 | 274,981,556 | 302,812,024 |
| 1567F | 977,810,827,294 | 981,523,833,176 | 978,954,476,445 | 978,984,848,378 |
| 1574F | 228,330 | 29,414,118,644,551,660 | 35,511,036,245,914 | 51,166,072,353,683 |
| 1580B | 1,334,498,244 | 123,221,869,874,820 | 624,486,447 | 634,227,280 |
| 1599J | 9,170 | 12,322,184 | 475,722 | 564,916 |
| 1569E | 2,080,621 | 1,344,652,839,825 | 28,664,383 | 314,421,572,899 |
| 1586F | 145,590,447 | 44,184,529,715 | 4,453,997,983 | 4,459,054,592 |
| 1556F | 14,256 | 29,408,855,404 | 329,414,216 | 28,447,327,936 |
| 1598F | 896 | 98,536,591 | 1,298,913 | 1,321,625 |
| 1620G | 2,156,032,471 | 48,229,717,663 | 10,033,525,628 | 10,058,693,310 |

## Method

Each runtime profile was measured three times and required identical metrics plus byte-exact oracle output. For the two abrupt state arms, the measurement-only copy replaces the final `std::_Exit(0)` with `std::exit(0)` after the same oracle write so LLVM and state reporters can flush; execution up to the checkpoint is unchanged. NativeTrace excludes library internals and inserted checkpoint-counter lines. StateSize recursively counts supported scalars, aggregates, strings, arrays, and container elements; shared compound objects are counted once, while instrumentation and runtime internals are excluded. StateLoad sums that same reachable-value count over the complete StateSize observation series.

## Files

- `profiles.json`: authoritative retained profiles and arm mappings.
- `static-profiles.csv`: Omega_CC for every byte-distinct source profile.
- `dynamic-profiles.csv`: NativeTrace, StateSize, and StateLoad for every independent execution.
- `arm-profile-map.csv`: arm-to-source and arm-to-execution mappings.
- `normalized-profiles.csv`: the shared long-form view for cross-benchmark analysis.
- `measure.py`: deterministic measurement generator.

The benchmark-local files above remain authoritative. Regenerate the common
view with:

```bash
python3 shared/metrics/scripts/normalize_profiles.py --config experiments/codecontests_reasoning_state_prediction/measurements/program-complexity/normalized-profiles-config.json
```
