# Aslan Nasdaq kuralları diğer endekslerde — 2026-11-05

Kod: [`research/aslan_nasdaq/indices.py`](../../research/aslan_nasdaq/indices.py), veri [`fetch_indices.py`](../../research/aslan_nasdaq/fetch_indices.py), PR #57, [Actions run](https://github.com/traxguo/ASGO.ai/actions/runs/42116503792). Kart: `cards/aslan_liquidity.md` ("Diğer endeksler").
Dondurulmuş AslanLiq2_1h yön filtreli, hiçbir ayar değişmedi. Geçme şartı (testten önce): her üç dönemde maliyet sonrası R > 0 ve maliyet öncesi R rastgele girişin üstünde. NAS100 satırları önceki raporla bire bir aynı çıktı (368 / 107 / 46 işlem).

## Ham çıktı
### NAS100 (round-trip cost 0.010%)
| Version | Period | Side | Trades | Win | BE win (after cost) | R before cost | Random entry R before cost | R after cost | PF | DD (1% risk) | Median stop |
|---|---|---|---|---|---|---|---|---|---|---|---|
| v2 1h bias | dev | long | 222 | 40.5% | 34.0% | +0.216 | +0.053 | +0.196 | 1.32 | 11% | 0.63% |
| v2 1h bias | dev | short | 146 | 30.1% | 34.0% | -0.112 | -0.105 | -0.132 | 0.82 | 27% | 0.69% |
| v2 1h bias | dev | all | 368 | 36.4% | 34.0% | +0.086 | -0.010 | +0.066 | 1.10 | 30% | 0.65% |
| v2 1h bias | val | long | 51 | 35.3% | 33.9% | +0.058 | -0.086 | +0.040 | 1.06 | 7% | 0.68% |
| v2 1h bias | val | short | 56 | 42.9% | 34.1% | +0.273 | -0.002 | +0.252 | 1.42 | 7% | 0.63% |
| v2 1h bias | val | all | 107 | 39.3% | 34.0% | +0.171 | -0.042 | +0.151 | 1.24 | 8% | 0.66% |
| v2 1h bias | holdout | long | 27 | 37.0% | 33.9% | +0.111 | +0.073 | +0.095 | 1.15 | 9% | 0.61% |
| v2 1h bias | holdout | short | 19 | 42.1% | 34.2% | +0.263 | -0.122 | +0.238 | 1.40 | 4% | 0.42% |
| v2 1h bias | holdout | all | 46 | 39.1% | 34.0% | +0.174 | -0.008 | +0.154 | 1.25 | 7% | 0.51% |

### NAS100 x2 cost (round-trip cost 0.020%)
| Version | Period | Side | Trades | Win | BE win (after cost) | R before cost | Random entry R before cost | R after cost | PF | DD (1% risk) | Median stop |
|---|---|---|---|---|---|---|---|---|---|---|---|
| v2 1h bias | dev | long | 222 | 40.5% | 34.7% | +0.216 | +0.053 | +0.176 | 1.28 | 12% | 0.63% |
| v2 1h bias | dev | short | 146 | 30.1% | 34.6% | -0.112 | -0.105 | -0.151 | 0.80 | 28% | 0.69% |
| v2 1h bias | dev | all | 368 | 36.4% | 34.7% | +0.086 | -0.010 | +0.046 | 1.07 | 32% | 0.65% |
| v2 1h bias | val | long | 51 | 35.3% | 34.5% | +0.058 | -0.086 | +0.022 | 1.03 | 7% | 0.68% |
| v2 1h bias | val | short | 56 | 42.9% | 34.8% | +0.273 | -0.002 | +0.230 | 1.38 | 7% | 0.63% |
| v2 1h bias | val | all | 107 | 39.3% | 34.7% | +0.171 | -0.042 | +0.131 | 1.20 | 8% | 0.66% |
| v2 1h bias | holdout | long | 27 | 37.0% | 34.4% | +0.111 | +0.073 | +0.079 | 1.12 | 9% | 0.61% |
| v2 1h bias | holdout | short | 19 | 42.1% | 35.0% | +0.263 | -0.122 | +0.214 | 1.35 | 4% | 0.42% |
| v2 1h bias | holdout | all | 46 | 39.1% | 34.6% | +0.174 | -0.008 | +0.135 | 1.21 | 7% | 0.51% |

### SPX500 (round-trip cost 0.010%)
| Version | Period | Side | Trades | Win | BE win (after cost) | R before cost | Random entry R before cost | R after cost | PF | DD (1% risk) | Median stop |
|---|---|---|---|---|---|---|---|---|---|---|---|
| v2 1h bias | dev | long | 213 | 36.2% | 34.2% | +0.082 | +0.059 | +0.054 | 1.08 | 20% | 0.49% |
| v2 1h bias | dev | short | 152 | 28.3% | 34.3% | -0.152 | -0.071 | -0.181 | 0.76 | 26% | 0.48% |
| v2 1h bias | dev | all | 365 | 32.9% | 34.3% | -0.015 | +0.005 | -0.044 | 0.94 | 28% | 0.49% |
| v2 1h bias | val | long | 63 | 34.9% | 34.2% | +0.031 | -0.087 | +0.006 | 1.01 | 10% | 0.50% |
| v2 1h bias | val | short | 45 | 28.9% | 34.3% | -0.147 | -0.024 | -0.176 | 0.76 | 13% | 0.45% |
| v2 1h bias | val | all | 108 | 32.4% | 34.2% | -0.043 | -0.061 | -0.070 | 0.90 | 21% | 0.48% |
| v2 1h bias | holdout | long | 21 | 38.1% | 34.3% | +0.143 | +0.016 | +0.115 | 1.18 | 3% | 0.42% |
| v2 1h bias | holdout | short | 20 | 35.0% | 34.6% | +0.050 | -0.089 | +0.013 | 1.02 | 6% | 0.30% |
| v2 1h bias | holdout | all | 41 | 36.6% | 34.4% | +0.098 | -0.035 | +0.066 | 1.10 | 7% | 0.36% |

### SPX500 x2 cost (round-trip cost 0.020%)
| Version | Period | Side | Trades | Win | BE win (after cost) | R before cost | Random entry R before cost | R after cost | PF | DD (1% risk) | Median stop |
|---|---|---|---|---|---|---|---|---|---|---|---|
| v2 1h bias | dev | long | 213 | 36.2% | 35.2% | +0.082 | +0.059 | +0.027 | 1.04 | 21% | 0.49% |
| v2 1h bias | dev | short | 152 | 28.3% | 35.3% | -0.152 | -0.071 | -0.210 | 0.72 | 30% | 0.48% |
| v2 1h bias | dev | all | 365 | 32.9% | 35.2% | -0.015 | +0.005 | -0.072 | 0.90 | 33% | 0.49% |
| v2 1h bias | val | long | 63 | 34.9% | 35.0% | +0.031 | -0.087 | -0.019 | 0.97 | 10% | 0.50% |
| v2 1h bias | val | short | 45 | 28.9% | 35.2% | -0.147 | -0.024 | -0.205 | 0.73 | 14% | 0.45% |
| v2 1h bias | val | all | 108 | 32.4% | 35.1% | -0.043 | -0.061 | -0.097 | 0.87 | 22% | 0.48% |
| v2 1h bias | holdout | long | 21 | 38.1% | 35.2% | +0.143 | +0.016 | +0.088 | 1.14 | 3% | 0.42% |
| v2 1h bias | holdout | short | 20 | 35.0% | 35.8% | +0.050 | -0.089 | -0.023 | 0.97 | 6% | 0.30% |
| v2 1h bias | holdout | all | 41 | 36.6% | 35.5% | +0.098 | -0.035 | +0.034 | 1.05 | 7% | 0.36% |

### GER40 (round-trip cost 0.010%)
| Version | Period | Side | Trades | Win | BE win (after cost) | R before cost | Random entry R before cost | R after cost | PF | DD (1% risk) | Median stop |
|---|---|---|---|---|---|---|---|---|---|---|---|
| v2 1h bias | dev | long | 169 | 35.5% | 34.2% | +0.049 | +0.042 | +0.024 | 1.04 | 20% | 0.59% |
| v2 1h bias | dev | short | 170 | 37.6% | 34.0% | +0.111 | -0.406 | +0.092 | 1.14 | 11% | 0.68% |
| v2 1h bias | dev | all | 339 | 36.6% | 34.1% | +0.080 | -0.183 | +0.058 | 1.09 | 22% | 0.64% |
| v2 1h bias | val | long | 54 | 33.3% | 34.1% | -0.022 | +0.074 | -0.045 | 0.94 | 14% | 0.57% |
| v2 1h bias | val | short | 50 | 30.0% | 34.4% | -0.091 | +0.002 | -0.124 | 0.83 | 13% | 0.43% |
| v2 1h bias | val | all | 104 | 31.7% | 34.2% | -0.055 | +0.039 | -0.083 | 0.88 | 21% | 0.53% |
| v2 1h bias | holdout | long | 13 | 30.8% | 34.3% | -0.077 | -0.137 | -0.106 | 0.85 | 5% | 0.46% |
| v2 1h bias | holdout | short | 6 | 83.3% | 34.3% | +1.500 | -0.109 | +1.472 | 9.54 | 1% | 0.51% |
| v2 1h bias | holdout | all | 19 | 47.4% | 34.3% | +0.421 | -0.128 | +0.392 | 1.72 | 5% | 0.46% |

### GER40 x2 cost (round-trip cost 0.020%)
| Version | Period | Side | Trades | Win | BE win (after cost) | R before cost | Random entry R before cost | R after cost | PF | DD (1% risk) | Median stop |
|---|---|---|---|---|---|---|---|---|---|---|---|
| v2 1h bias | dev | long | 169 | 35.5% | 35.0% | +0.049 | +0.042 | -0.002 | 1.00 | 21% | 0.59% |
| v2 1h bias | dev | short | 170 | 37.6% | 34.6% | +0.111 | -0.406 | +0.073 | 1.11 | 11% | 0.68% |
| v2 1h bias | dev | all | 339 | 36.6% | 34.8% | +0.080 | -0.183 | +0.036 | 1.05 | 25% | 0.64% |
| v2 1h bias | val | long | 54 | 33.3% | 34.8% | -0.022 | +0.074 | -0.067 | 0.91 | 14% | 0.57% |
| v2 1h bias | val | short | 50 | 30.0% | 35.6% | -0.091 | +0.002 | -0.158 | 0.79 | 14% | 0.43% |
| v2 1h bias | val | all | 104 | 31.7% | 35.2% | -0.055 | +0.039 | -0.110 | 0.85 | 22% | 0.53% |
| v2 1h bias | holdout | long | 13 | 30.8% | 35.3% | -0.077 | -0.137 | -0.135 | 0.82 | 6% | 0.46% |
| v2 1h bias | holdout | short | 6 | 83.3% | 35.2% | +1.500 | -0.109 | +1.444 | 9.10 | 1% | 0.51% |
| v2 1h bias | holdout | all | 19 | 47.4% | 35.2% | +0.421 | -0.128 | +0.364 | 1.65 | 5% | 0.46% |

### UK100 (round-trip cost 0.015%)
| Version | Period | Side | Trades | Win | BE win (after cost) | R before cost | Random entry R before cost | R after cost | PF | DD (1% risk) | Median stop |
|---|---|---|---|---|---|---|---|---|---|---|---|
| v2 1h bias | dev | long | 206 | 33.0% | 34.7% | -0.013 | -0.040 | -0.054 | 0.92 | 22% | 0.45% |
| v2 1h bias | dev | short | 203 | 31.0% | 34.6% | -0.082 | -0.026 | -0.121 | 0.83 | 23% | 0.45% |
| v2 1h bias | dev | all | 409 | 32.0% | 34.7% | -0.047 | -0.033 | -0.087 | 0.88 | 33% | 0.45% |
| v2 1h bias | val | long | 64 | 45.3% | 34.7% | +0.358 | +0.208 | +0.316 | 1.55 | 5% | 0.43% |
| v2 1h bias | val | short | 30 | 13.3% | 35.0% | -0.600 | -0.233 | -0.649 | 0.28 | 19% | 0.35% |
| v2 1h bias | val | all | 94 | 35.1% | 34.8% | +0.052 | +0.067 | +0.008 | 1.01 | 18% | 0.41% |
| v2 1h bias | holdout | long | 36 | 30.6% | 34.8% | -0.085 | -0.223 | -0.128 | 0.82 | 10% | 0.42% |
| v2 1h bias | holdout | short | 8 | 0.0% | 34.3% | -1.000 | +0.070 | -1.030 | 0.00 | 8% | 0.50% |
| v2 1h bias | holdout | all | 44 | 25.0% | 34.7% | -0.251 | -0.171 | -0.292 | 0.63 | 16% | 0.43% |

### UK100 x2 cost (round-trip cost 0.030%)
| Version | Period | Side | Trades | Win | BE win (after cost) | R before cost | Random entry R before cost | R after cost | PF | DD (1% risk) | Median stop |
|---|---|---|---|---|---|---|---|---|---|---|---|
| v2 1h bias | dev | long | 206 | 33.0% | 36.0% | -0.013 | -0.040 | -0.094 | 0.87 | 26% | 0.45% |
| v2 1h bias | dev | short | 203 | 31.0% | 36.0% | -0.082 | -0.026 | -0.160 | 0.79 | 29% | 0.45% |
| v2 1h bias | dev | all | 409 | 32.0% | 36.0% | -0.047 | -0.033 | -0.127 | 0.83 | 43% | 0.45% |
| v2 1h bias | val | long | 64 | 45.3% | 36.1% | +0.358 | +0.208 | +0.275 | 1.46 | 5% | 0.43% |
| v2 1h bias | val | short | 30 | 13.3% | 36.6% | -0.600 | -0.233 | -0.697 | 0.26 | 20% | 0.35% |
| v2 1h bias | val | all | 94 | 35.1% | 36.3% | +0.052 | +0.067 | -0.035 | 0.95 | 19% | 0.41% |
| v2 1h bias | holdout | long | 36 | 30.6% | 36.2% | -0.085 | -0.223 | -0.172 | 0.77 | 11% | 0.42% |
| v2 1h bias | holdout | short | 8 | 0.0% | 35.4% | -1.000 | +0.070 | -1.061 | 0.00 | 8% | 0.50% |
| v2 1h bias | holdout | all | 44 | 25.0% | 36.1% | -0.251 | -0.171 | -0.333 | 0.59 | 17% | 0.43% |

### JPN225 (round-trip cost 0.025%)
| Version | Period | Side | Trades | Win | BE win (after cost) | R before cost | Random entry R before cost | R after cost | PF | DD (1% risk) | Median stop |
|---|---|---|---|---|---|---|---|---|---|---|---|
| v2 1h bias | dev | long | 200 | 32.5% | 34.9% | -0.025 | +0.024 | -0.072 | 0.90 | 28% | 0.61% |
| v2 1h bias | dev | short | 193 | 32.1% | 35.1% | -0.033 | -0.059 | -0.085 | 0.88 | 31% | 0.62% |
| v2 1h bias | dev | all | 393 | 32.3% | 35.0% | -0.029 | -0.016 | -0.079 | 0.89 | 46% | 0.62% |
| v2 1h bias | val | long | 57 | 42.1% | 34.7% | +0.253 | +0.018 | +0.213 | 1.35 | 9% | 0.68% |
| v2 1h bias | val | short | 26 | 26.9% | 34.4% | -0.192 | -0.202 | -0.224 | 0.70 | 9% | 0.95% |
| v2 1h bias | val | all | 83 | 37.3% | 34.6% | +0.114 | -0.051 | +0.076 | 1.12 | 13% | 0.77% |
| v2 1h bias | holdout | long | 30 | 36.7% | 34.2% | +0.099 | +0.131 | +0.074 | 1.11 | 7% | 1.08% |
| v2 1h bias | holdout | short | 24 | 33.3% | 34.5% | +0.000 | -0.178 | -0.036 | 0.95 | 6% | 0.90% |
| v2 1h bias | holdout | all | 54 | 35.2% | 34.3% | +0.055 | -0.007 | +0.025 | 1.04 | 10% | 1.03% |

### JPN225 x2 cost (round-trip cost 0.050%)
| Version | Period | Side | Trades | Win | BE win (after cost) | R before cost | Random entry R before cost | R after cost | PF | DD (1% risk) | Median stop |
|---|---|---|---|---|---|---|---|---|---|---|---|
| v2 1h bias | dev | long | 200 | 32.5% | 36.5% | -0.025 | +0.024 | -0.119 | 0.84 | 33% | 0.61% |
| v2 1h bias | dev | short | 193 | 32.1% | 36.8% | -0.033 | -0.059 | -0.137 | 0.82 | 37% | 0.62% |
| v2 1h bias | dev | all | 393 | 32.3% | 36.6% | -0.029 | -0.016 | -0.128 | 0.83 | 54% | 0.62% |
| v2 1h bias | val | long | 57 | 42.1% | 36.0% | +0.253 | +0.018 | +0.173 | 1.27 | 9% | 0.68% |
| v2 1h bias | val | short | 26 | 26.9% | 35.5% | -0.192 | -0.202 | -0.257 | 0.67 | 9% | 0.95% |
| v2 1h bias | val | all | 83 | 37.3% | 35.8% | +0.114 | -0.051 | +0.038 | 1.06 | 13% | 0.77% |
| v2 1h bias | holdout | long | 30 | 36.7% | 35.0% | +0.099 | +0.131 | +0.049 | 1.07 | 8% | 1.08% |
| v2 1h bias | holdout | short | 24 | 33.3% | 35.8% | +0.000 | -0.178 | -0.073 | 0.90 | 6% | 0.90% |
| v2 1h bias | holdout | all | 54 | 35.2% | 35.3% | +0.055 | -0.007 | -0.005 | 0.99 | 11% | 1.03% |

## Verdict (pass: net > 0 and gross above random in dev, val and holdout)

### NAS100: PASS
- dev: 368 trades (6.1/month), net +0.066R, gross +0.086 vs random -0.010 -> ok
- val: 107 trades (7.2/month), net +0.151R, gross +0.171 vs random -0.042 -> ok
- holdout: 46 trades (7.7/month), net +0.154R, gross +0.174 vs random -0.008 -> ok

### SPX500: FAIL
- dev: 365 trades (6.1/month), net -0.044R, gross -0.015 vs random +0.005 -> FAIL
- val: 108 trades (7.2/month), net -0.070R, gross -0.043 vs random -0.061 -> FAIL
- holdout: 41 trades (6.8/month), net +0.066R, gross +0.098 vs random -0.035 -> ok
- 257/457 trade days shared with NAS100 (56%); daily net R correlation on shared days +0.48, on all days +0.27

### GER40: FAIL
- dev: 339 trades (5.6/month), net +0.058R, gross +0.080 vs random -0.183 -> ok
- val: 104 trades (7.0/month), net -0.083R, gross -0.055 vs random +0.039 -> FAIL
- holdout: 19 trades (3.2/month), net +0.392R, gross +0.421 vs random -0.128 -> ok
- 142/429 trade days shared with NAS100 (33%); daily net R correlation on shared days +0.33, on all days +0.11

### UK100: FAIL
- dev: 409 trades (6.8/month), net -0.087R, gross -0.047 vs random -0.033 -> FAIL
- val: 94 trades (6.3/month), net +0.008R, gross +0.052 vs random +0.067 -> FAIL
- holdout: 44 trades (7.3/month), net -0.292R, gross -0.251 vs random -0.171 -> FAIL
- 156/501 trade days shared with NAS100 (31%); daily net R correlation on shared days +0.22, on all days +0.07

### JPN225: FAIL
- dev: 393 trades (6.5/month), net -0.079R, gross -0.029 vs random -0.016 -> FAIL
- val: 83 trades (5.6/month), net +0.076R, gross +0.114 vs random -0.051 -> ok
- holdout: 54 trades (9.0/month), net +0.025R, gross +0.055 vs random -0.007 -> ok
- 162/490 trade days shared with NAS100 (33%); daily net R correlation on shared days +0.26, on all days +0.10
