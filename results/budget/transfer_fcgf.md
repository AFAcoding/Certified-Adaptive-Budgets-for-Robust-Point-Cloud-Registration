# Transfer to FCGF descriptors (configurations certified on FPFH validation)

| set | estimator | order | certificate | ladder | RR % | full RR % | loss [UB] pp | non-inferior | speed-up [95% CI] | risk % |
|---|---|---|---|---|---|---|---|---|---|---|
| fcgf_3DMatch | sc2 | ratio | mondrian | 500-4000 | 90.02 | 92.36 | 2.34 [3.45] | False | 11.08× [9.72, 12.72] | 3.20 |
| fcgf_3DMatch | sc2 | ratio | marginal | 500-4000 | 89.90 | 92.36 | 2.46 [3.57] | False | 12.59× [11.09, 14.30] | 3.33 |
| fcgf_3DMatch | turbo | ratio | mondrian | 500-4000 | 89.90 | 92.12 | 2.22 [3.33] | False | 9.68× [8.50, 11.24] | 3.20 |
| fcgf_3DMatch | turbo | ratio | marginal | 250-500-4000 | 87.93 | 92.12 | 4.19 [5.67] | False | 16.39× [13.52, 20.54] | 5.30 |
| fcgf_3DMatch | sc2 | compat | mondrian | 500-4000 | 90.15 | 92.36 | 2.22 [3.20] | False | 9.79× [8.54, 11.25] | 2.71 |
| fcgf_3DMatch | sc2 | compat | marginal | 250-4000 | 87.93 | 92.36 | 4.43 [5.79] | False | 17.35× [14.74, 20.64] | 5.42 |
| fcgf_3DMatch | turbo | compat | mondrian | 500-4000 | 90.02 | 92.12 | 2.09 [3.20] | False | 8.65× [7.63, 9.97] | 2.71 |
| fcgf_3DMatch | turbo | compat | marginal | 500-4000 | 89.04 | 92.12 | 3.08 [4.31] | False | 11.10× [9.85, 12.51] | 3.69 |
| fcgf_3DLoMatch | sc2 | ratio | mondrian | 500-4000 | 53.09 | 57.35 | 4.26 [5.84] | False | 2.77× [2.55, 3.04] | 6.62 |
| fcgf_3DLoMatch | sc2 | ratio | marginal | 500-4000 | 50.73 | 57.35 | 6.62 [8.42] | False | 3.84× [3.45, 4.30] | 8.98 |
| fcgf_3DLoMatch | turbo | ratio | mondrian | 500-4000 | 52.86 | 58.02 | 5.16 [6.73] | False | 2.90× [2.65, 3.19] | 6.40 |
| fcgf_3DLoMatch | turbo | ratio | marginal | 250-500-4000 | 50.06 | 58.02 | 7.97 [9.76] | False | 3.58× [3.22, 4.00] | 9.32 |
| fcgf_3DLoMatch | sc2 | compat | mondrian | 500-4000 | 53.09 | 57.35 | 4.26 [5.61] | False | 2.54× [2.34, 2.77] | 5.72 |
| fcgf_3DLoMatch | sc2 | compat | marginal | 250-4000 | 47.36 | 57.35 | 9.99 [12.01] | False | 4.64× [4.09, 5.31] | 11.78 |
| fcgf_3DLoMatch | turbo | compat | mondrian | 500-4000 | 54.55 | 58.02 | 3.48 [4.83] | False | 2.29× [2.13, 2.47] | 4.71 |
| fcgf_3DLoMatch | turbo | compat | marginal | 500-4000 | 50.28 | 58.02 | 7.74 [9.54] | False | 3.72× [3.36, 4.13] | 9.20 |
| fcgf_kitti_test | sc2 | ratio | mondrian | 250-2000-4000 | 94.24 | 94.96 | 0.72 [1.44] | False | 1.21× [1.12, 1.33] | 0.72 |
| fcgf_kitti_test | sc2 | ratio | marginal | full | 94.96 | 94.96 | 0.00 [0.00] | True | 1.00× [1.00, 1.00] | 0.00 |
| fcgf_kitti_test | turbo | ratio | mondrian | 250-1000-2000-4000 | 93.88 | 94.96 | 1.08 [2.16] | False | 0.78× [0.76, 0.81] | 1.08 |
| fcgf_kitti_test | turbo | ratio | marginal | 250-1000-2000-4000 | 92.09 | 94.96 | 2.88 [4.68] | False | 24.66× [16.89, 37.73] | 2.88 |
| fcgf_kitti_test | sc2 | compat | mondrian | 250-2000-4000 | 94.96 | 94.96 | 0.00 [0.00] | True | 0.76× [0.76, 0.77] | 0.00 |
| fcgf_kitti_test | sc2 | compat | marginal | 250-1000-2000-4000 | 93.53 | 94.96 | 1.44 [2.88] | False | 21.92× [14.98, 33.82] | 1.80 |
| fcgf_kitti_test | turbo | compat | mondrian | 250-2000-4000 | 94.96 | 94.96 | 0.00 [0.00] | True | 0.77× [0.77, 0.78] | 0.00 |
| fcgf_kitti_test | turbo | compat | marginal | 500-2000-4000 | 93.53 | 94.96 | 1.44 [2.88] | False | 15.76× [12.22, 19.80] | 1.44 |
