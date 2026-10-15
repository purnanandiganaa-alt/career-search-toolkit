"""Canonical application states, shared by set_status.py and pipeline_summary.py."""

CANONICAL_STATES = [
    "Evaluated",  # job-fit-eval has scored it, not yet drafted
    "Drafted",    # resume/cover letter tailored, not yet sent
    "Applied",    # sent -- user confirmed they actually clicked submit
    "Responded",  # company replied
    "Interview",  # in interview process
    "Offer",      # offer received
    "Rejected",   # rejected by company
    "Discarded",  # user decided not to pursue further
    "SKIP",       # evaluated but not worth applying (e.g. fit score too low)
]
