import Submission.EndStatement
import Submission.ThreeSum.TernaryFinalSolver

/-- Complete deterministic 3SUM bound in the trusted benchmark model. -/
theorem Race.bound :
    EndStatement.ThreeSum.SolvedInTime ((1920279461 : Rat) / 1000000000) := by
  exact ThreeSum.solvedInTime_1920279461_1000000000
