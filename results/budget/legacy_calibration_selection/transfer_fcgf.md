# Transfer to FCGF descriptors (configurations certified on FPFH validation)

| set | estimator | order | certificate | ladder | RR % | full RR % | loss [UB] pp | non-inferior | speed-up [95% CI] | risk % |
|---|---|---|---|---|---|---|---|---|---|---|
| fcgf_3DMatch | sc2 | ratio | mondrian | 250-4000 | 89.04 | 92.36 | 3.33 [4.56] | False | 11.72× [9.82, 14.48] | 3.94 |
| fcgf_3DMatch | sc2 | ratio | marginal | x4 | 87.93 | 92.36 | 4.43 [5.79] | False | 23.99× [19.50, 30.04] | 5.17 |
| fcgf_3DMatch | turbo | ratio | mondrian | x4 | 89.04 | 92.12 | 3.08 [4.43] | False | 17.95× [14.85, 22.26] | 4.19 |
| fcgf_3DMatch | turbo | ratio | marginal | x4 | 87.81 | 92.12 | 4.31 [5.79] | False | 23.07× [19.03, 28.31] | 5.42 |
| fcgf_3DMatch | sc2 | compat | mondrian | 250-4000 | 88.67 | 92.36 | 3.69 [5.05] | False | 13.21× [11.24, 15.78] | 4.68 |
| fcgf_3DMatch | sc2 | compat | marginal | 250-4000 | 87.93 | 92.36 | 4.43 [5.79] | False | 17.35× [14.74, 20.64] | 5.42 |
| fcgf_3DMatch | turbo | compat | mondrian | 250-4000 | 88.05 | 92.12 | 4.06 [5.30] | False | 12.09× [10.32, 14.39] | 4.56 |
| fcgf_3DMatch | turbo | compat | marginal | 250-4000 | 87.44 | 92.12 | 4.68 [6.03] | False | 15.50× [13.21, 18.38] | 5.17 |
| fcgf_3DLoMatch | sc2 | ratio | mondrian | 250-4000 | 52.41 | 57.35 | 4.94 [6.29] | False | 2.10× [1.96, 2.28] | 5.84 |
| fcgf_3DLoMatch | sc2 | ratio | marginal | x4 | 48.60 | 57.35 | 8.75 [10.66] | False | 5.68× [4.97, 6.56] | 10.77 |
| fcgf_3DLoMatch | turbo | ratio | mondrian | x4 | 53.54 | 58.02 | 4.49 [6.06] | False | 3.76× [3.40, 4.22] | 6.29 |
| fcgf_3DLoMatch | turbo | ratio | marginal | x4 | 50.06 | 58.02 | 7.97 [9.76] | False | 6.46× [5.62, 7.55] | 9.65 |
| fcgf_3DLoMatch | sc2 | compat | mondrian | 250-4000 | 51.07 | 57.35 | 6.29 [7.97] | False | 3.05× [2.77, 3.37] | 8.08 |
| fcgf_3DLoMatch | sc2 | compat | marginal | 250-4000 | 47.36 | 57.35 | 9.99 [12.01] | False | 4.64× [4.09, 5.31] | 11.78 |
| fcgf_3DLoMatch | turbo | compat | mondrian | 250-4000 | 53.31 | 58.02 | 4.71 [6.29] | False | 2.51× [2.31, 2.73] | 6.29 |
| fcgf_3DLoMatch | turbo | compat | marginal | 250-4000 | 48.60 | 58.02 | 9.43 [11.34] | False | 3.97× [3.55, 4.46] | 11.00 |
| fcgf_kitti_test | sc2 | ratio | mondrian | 500-2000-4000 | 94.60 | 94.96 | 0.36 [1.08] | False | 1.05× [0.98, 1.14] | 0.36 |
| fcgf_kitti_test | sc2 | ratio | marginal | 500-2000-4000 | 94.60 | 94.96 | 0.36 [1.08] | False | 1.09× [1.02, 1.19] | 0.36 |
| fcgf_kitti_test | turbo | ratio | mondrian | 500-2000-4000 | 93.88 | 94.96 | 1.08 [2.16] | False | 1.54× [1.39, 1.75] | 1.08 |
| fcgf_kitti_test | turbo | ratio | marginal | doubling | 93.88 | 94.96 | 1.08 [2.16] | False | 0.79× [0.77, 0.83] | 1.08 |
| fcgf_kitti_test | sc2 | compat | mondrian | 250-2000-4000 | 93.53 | 94.96 | 1.44 [2.88] | False | 18.40× [12.94, 27.39] | 1.80 |
| fcgf_kitti_test | sc2 | compat | marginal | 500-2000-4000 | 93.88 | 94.96 | 1.08 [2.16] | False | 15.28× [11.82, 19.94] | 1.08 |
| fcgf_kitti_test | turbo | compat | mondrian | 250-2000-4000 | 93.53 | 94.96 | 1.44 [2.88] | False | 17.21× [12.32, 24.97] | 1.80 |
| fcgf_kitti_test | turbo | compat | marginal | 250-2000-4000 | 93.53 | 94.96 | 1.44 [2.88] | False | 17.21× [12.32, 24.97] | 1.80 |
