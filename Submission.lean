import Submission.EndStatement
import Submission.ThreeSum.TernaryFinalSolver

/-- Complete deterministic 3SUM bound in the trusted benchmark model. -/
theorem Race.bound :
    EndStatement.ThreeSum.SolvedInTime ((4800698571997281331 : Rat) / 2500000000000000000) := by
  exact ThreeSum.solvedInTime_4800698571997281331_2500000000000000000
