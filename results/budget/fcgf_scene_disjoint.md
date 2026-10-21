# Scene-disjoint FCGF evaluation (cross-fitting over scenes)

Controller fitted and certified on the other scenes only; every pair tested once; pooled over folds.

| test set | estimator | order | certificate | folds: ladder | RR % | full RR % | loss [UB] pp | non-inferior | offline speed-up [95% CI] | risk % |
|---|---|---|---|---|---|---|---|---|---|---|
| fcgf_3DMatch | sc2 | ratio | marginal | 500-4000/500-4000/250-500-4000/250-4000 | 92.17 | 92.54 | 0.37 [0.74] | True | 4.34× [4.00, 4.75] | 0.68 |
| fcgf_3DLoMatch | sc2 | ratio | marginal | 500-4000/500-4000/250-500-4000/250-4000 | 57.55 | 58.23 | 0.67 [1.07] | True | 1.20× [1.17, 1.22] | 0.79 |
| fcgf_3DMatch | sc2 | ratio | mondrian | 250-500-4000/250-4000/250-4000/250-4000 | 92.48 | 92.54 | 0.06 [0.25] | True | 1.60× [1.54, 1.66] | 0.12 |
| fcgf_3DLoMatch | sc2 | ratio | mondrian | 250-500-4000/250-4000/250-4000/250-4000 | 58.17 | 58.23 | 0.06 [0.22] | True | 1.00× [0.99, 1.01] | 0.11 |
| fcgf_3DMatch | turbo | ratio | marginal | 500-4000/250-4000/500-4000/500-4000 | 92.11 | 92.61 | 0.49 [0.86] | True | 4.14× [3.85, 4.49] | 0.68 |
| fcgf_3DLoMatch | turbo | ratio | marginal | 500-4000/250-4000/500-4000/500-4000 | 57.66 | 58.39 | 0.73 [1.18] | True | 1.24× [1.21, 1.27] | 1.01 |
| fcgf_3DMatch | turbo | ratio | mondrian | 500-4000/250-500-4000/500-4000/250-4000 | 92.36 | 92.61 | 0.25 [0.55] | True | 1.31× [1.29, 1.35] | 0.37 |
| fcgf_3DLoMatch | turbo | ratio | mondrian | 500-4000/250-500-4000/500-4000/250-4000 | 58.28 | 58.39 | 0.11 [0.28] | True | 1.02× [1.01, 1.03] | 0.11 |
| fcgf_3DMatch | sc2 | compat | marginal | 250-4000/500-4000/500-4000/500-4000 | 92.05 | 92.54 | 0.49 [0.86] | True | 4.04× [3.74, 4.39] | 0.62 |
| fcgf_3DLoMatch | sc2 | compat | marginal | 250-4000/500-4000/500-4000/500-4000 | 57.38 | 58.23 | 0.84 [1.29] | True | 1.26× [1.22, 1.29] | 1.01 |
| fcgf_3DMatch | sc2 | compat | mondrian | x4/500-4000/500-4000/500-4000 | 92.36 | 92.54 | 0.18 [0.49] | True | 2.92× [2.74, 3.12] | 0.31 |
| fcgf_3DLoMatch | sc2 | compat | mondrian | x4/500-4000/500-4000/500-4000 | 58.06 | 58.23 | 0.17 [0.39] | True | 1.06× [1.04, 1.08] | 0.22 |
| fcgf_3DMatch | turbo | compat | marginal | 500-4000/500-4000/250-4000/500-4000 | 92.24 | 92.61 | 0.37 [0.68] | True | 4.28× [3.96, 4.64] | 0.49 |
| fcgf_3DLoMatch | turbo | compat | marginal | 500-4000/500-4000/250-4000/500-4000 | 57.94 | 58.39 | 0.45 [0.79] | True | 1.25× [1.22, 1.28] | 0.67 |
| fcgf_3DMatch | turbo | compat | mondrian | 250-4000/500-4000/500-4000/250-4000 | 92.42 | 92.61 | 0.18 [0.49] | True | 2.65× [2.51, 2.84] | 0.31 |
| fcgf_3DLoMatch | turbo | compat | mondrian | 250-4000/500-4000/500-4000/250-4000 | 58.23 | 58.39 | 0.17 [0.45] | True | 1.08× [1.06, 1.10] | 0.34 |
| fcgf_kitti_test | sc2 | ratio | marginal | full/full/500-2000-4000 | 93.86 | 93.86 | 0.00 [0.00] | True | 1.02× [1.00, 1.04] | 0.00 |
| fcgf_kitti_test | sc2 | ratio | mondrian | full/full/full | 93.86 | 93.86 | 0.00 [0.00] | True | 1.00× [1.00, 1.00] | 0.00 |
| fcgf_kitti_test | turbo | ratio | marginal | full/full/x4 | 93.86 | 93.86 | 0.00 [0.00] | True | 0.98× [0.98, 0.98] | 0.00 |
| fcgf_kitti_test | turbo | ratio | mondrian | full/full/full | 93.86 | 93.86 | 0.00 [0.00] | True | 1.00× [1.00, 1.00] | 0.00 |
| fcgf_kitti_test | sc2 | compat | marginal | full/500-2000-4000/full | 93.86 | 93.86 | 0.00 [0.00] | True | 0.92× [0.91, 0.92] | 0.00 |
| fcgf_kitti_test | sc2 | compat | mondrian | full/full/full | 93.86 | 93.86 | 0.00 [0.00] | True | 1.00× [1.00, 1.00] | 0.00 |
| fcgf_kitti_test | turbo | compat | marginal | full/full/500-4000 | 93.86 | 93.86 | 0.00 [0.00] | True | 1.00× [0.99, 1.01] | 0.00 |
| fcgf_kitti_test | turbo | compat | mondrian | full/full/full | 93.86 | 93.86 | 0.00 [0.00] | True | 1.00× [1.00, 1.00] | 0.00 |
