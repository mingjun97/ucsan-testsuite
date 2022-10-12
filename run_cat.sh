rm -rf ./outputs
mkdir outputs
# TAINT_OPTIONS="debug=1 output_dir=/workdir/tmp/outputs taint_file=./input-link-head" ./a.out
TAINT_OPTIONS="debug=1 output_dir=/workdir/tmp/outputs" ./a.out