from __future__ import print_function
import sys
import subprocess

if __name__ == "__main__":

    if len(sys.argv) < 2:
        print("Usage: python submit_meso_jobs.py firstinpfile.inp [secondinpfile.inp ...]")
        sys.exit(1)

    with open("sbatch_meso_template.slrm", "r") as f:
        slurm_job_template = f.read()

    for input_filename in sys.argv[1:]: # it supports any number of files, you can call it with python submit_meso_jobs.py *.inp
        print("Preparing file", input_filename)

        slurm_job_template_filled = slurm_job_template.format(input_filename=input_filename)
        #print(slurm_job_template_filled)

        # calls sbatch to submit a job for each input file
        proc = subprocess.Popen("sbatch", stdin=subprocess.PIPE)
        try:
            outs, errs = proc.communicate(slurm_job_template_filled.encode("ascii"), timeout=30)
        except subprocess.TimeoutExpired:
            proc.kill()
            outs, errs = proc.communicate()
