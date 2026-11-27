# 2026-11-27 — exp-083 cancellation status

- Kaggle kernel: accelra/exp-083-source-owned-exp-065-with-v20-chemistry.
- Command from the Git checkout: `& '..\..\.venv\Scripts\python.exe' -m kaggle kernels status accelra/exp-083-source-owned-exp-065-with-v20-chemistry`.
- Observed status: `CANCEL_ACKNOWLEDGED`.
- No version-5 receipt, integrated-verifier result, output archive, or Kaggle score was produced.
- The earlier local archive in `experiments/exp-083/receipts/source-assembled-v20-portfolio.json` is a component composition only; its verifier GM `30.35107` is a projection.
- Decision: close exp-083. Use exp-074's independently verified V20 chemistry output in later portfolios; do not relaunch the full source rebuild without a new reason.
