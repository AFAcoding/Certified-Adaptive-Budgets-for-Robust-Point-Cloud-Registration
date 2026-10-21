# Scene-disjoint FCGF evaluation (cross-fitting over scenes)

Controller fitted and certified on the other scenes only; every pair tested once; pooled over folds.

| test set | estimator | order | certificate | folds: ladder | RR % | full RR % | loss [UB] pp | non-inferior | offline speed-up [95% CI] | risk % |
|---|---|---|---|---|---|---|---|---|---|---|
| fcgf_3DMatch | sc2 | ratio | marginal | 500-4000/250-2000-4000/500-4000/500-4000 | 92.24 | 92.54 | 0.31 [0.74] | True | 4.50× [4.16, 4.92] | 0.74 |
| fcgf_3DLoMatch | sc2 | ratio | marginal | 500-4000/250-2000-4000/500-4000/500-4000 | 57.72 | 58.23 | 0.51 [0.95] | True | 1.25× [1.21, 1.28] | 0.84 |
| fcgf_3DMatch | sc2 | ratio | mondrian | 250-4000/500-4000/250-4000/500-4000 | 92.54 | 92.54 | 0.00 [0.25] | True | 2.06× [1.97, 2.18] | 0.18 |
| fcgf_3DLoMatch | sc2 | ratio | mondrian | 250-4000/500-4000/250-4000/500-4000 | 58.06 | 58.23 | 0.17 [0.45] | True | 1.05× [1.04, 1.07] | 0.39 |
| fcgf_3DMatch | turbo | ratio | marginal | 250-4000/250-4000/250-4000/500-4000 | 91.68 | 92.61 | 0.92 [1.42] | False | 4.78× [4.40, 5.23] | 1.23 |
| fcgf_3DLoMatch | turbo | ratio | marginal | 250-4000/250-4000/250-4000/500-4000 | 57.83 | 58.39 | 0.56 [0.95] | True | 1.29× [1.26, 1.33] | 0.84 |
| fcgf_3DMatch | turbo | ratio | mondrian | 250-4000/250-4000/250-4000/500-4000 | 92.42 | 92.61 | 0.18 [0.43] | True | 2.20× [2.09, 2.33] | 0.25 |
| fcgf_3DLoMatch | turbo | ratio | mondrian | 250-4000/250-4000/250-4000/500-4000 | 58.28 | 58.39 | 0.11 [0.28] | True | 1.07× [1.06, 1.09] | 0.17 |
| fcgf_3DMatch | sc2 | compat | marginal | 500-4000/500-4000/250-4000/x4 | 92.11 | 92.54 | 0.43 [0.86] | True | 4.64× [4.27, 5.07] | 0.74 |
| fcgf_3DLoMatch | sc2 | compat | marginal | 500-4000/500-4000/250-4000/x4 | 57.66 | 58.23 | 0.56 [0.95] | True | 1.30× [1.26, 1.34] | 0.84 |
| fcgf_3DMatch | sc2 | compat | mondrian | x4/x4/500-4000/250-4000 | 92.42 | 92.54 | 0.12 [0.43] | True | 2.95× [2.76, 3.17] | 0.31 |
| fcgf_3DLoMatch | sc2 | compat | mondrian | x4/x4/500-4000/250-4000 | 58.06 | 58.23 | 0.17 [0.45] | True | 1.06× [1.04, 1.08] | 0.34 |
| fcgf_3DMatch | turbo | compat | marginal | 500-4000/500-4000/500-4000/250-4000 | 92.17 | 92.61 | 0.43 [0.80] | True | 4.34× [4.03, 4.71] | 0.62 |
| fcgf_3DLoMatch | turbo | compat | marginal | 500-4000/500-4000/500-4000/250-4000 | 58.06 | 58.39 | 0.34 [0.73] | True | 1.25× [1.22, 1.29] | 0.67 |
| fcgf_3DMatch | turbo | compat | mondrian | 250-4000/250-4000/500-4000/500-4000 | 92.36 | 92.61 | 0.25 [0.49] | True | 2.68× [2.53, 2.85] | 0.31 |
| fcgf_3DLoMatch | turbo | compat | mondrian | 250-4000/250-4000/500-4000/500-4000 | 58.23 | 58.39 | 0.17 [0.39] | True | 1.09× [1.07, 1.11] | 0.28 |
| fcgf_kitti_test | sc2 | ratio | marginal | full/250-1000-2000-4000/500-4000 | 93.50 | 93.86 | 0.36 [0.90] | True | 1.37× [1.33, 1.42] | 0.54 |
| fcgf_kitti_test | sc2 | ratio | mondrian | full/full/full | 93.86 | 93.86 | 0.00 [0.00] | True | 1.00× [1.00, 1.00] | 0.00 |
| fcgf_kitti_test | turbo | ratio | marginal | full/x4/500-4000 | 93.32 | 93.86 | 0.54 [1.26] | False | 1.34× [1.31, 1.38] | 0.72 |
| fcgf_kitti_test | turbo | ratio | mondrian | full/full/full | 93.86 | 93.86 | 0.00 [0.00] | True | 1.00× [1.00, 1.00] | 0.00 |
| fcgf_kitti_test | sc2 | compat | marginal | full/fixed-1000/500-4000 | 93.32 | 93.86 | 0.54 [1.08] | False | 1.50× [1.46, 1.54] | 0.54 |
| fcgf_kitti_test | sc2 | compat | mondrian | full/full/full | 93.86 | 93.86 | 0.00 [0.00] | True | 1.00× [1.00, 1.00] | 0.00 |
| fcgf_kitti_test | turbo | compat | marginal | full/fixed-1000/full | 93.14 | 93.86 | 0.72 [1.44] | False | 1.36× [1.34, 1.37] | 0.72 |
| fcgf_kitti_test | turbo | compat | mondrian | full/full/full | 93.86 | 93.86 | 0.00 [0.00] | True | 1.00× [1.00, 1.00] | 0.00 |
