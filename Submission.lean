import Submission.EndStatement
import Submission.ThreeSum.TernaryFinalSolver

/-- Complete deterministic 3SUM bound in the trusted benchmark model. -/
theorem Race.bound :
    EndStatement.ThreeSum.SolvedInTime ((192027945701 : Rat) / 100000000000) := by
  exact ThreeSum.solvedInTime_192027945701_100000000000
