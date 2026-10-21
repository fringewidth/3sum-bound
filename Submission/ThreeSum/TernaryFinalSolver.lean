import Submission.ThreeSum.TernaryProfileFastExecution

noncomputable section
namespace ThreeSum
open Light TernaryConcreteProfile

/-- The concrete hybrid executable solves the original distinct-position
task at every input size and supplied magnitude bound. -/
theorem ternary_hybrid_solves {κ : ℕ} (P : Profile κ) :
    Solves s3Task P.hybridProgram P.hybridMain P.hybridTime P.hybridNeed :=
  TernarySolverEndBridge.hybrid_solves P.fastExecution

/-- The original deterministic word-RAM benchmark, for every fixed
polynomial magnitude exponent, at the exact rational exponent 4800698571997281331/2500000000000000000. -/
theorem solvedInTime_4800698571997281331_2500000000000000000 :
    EndStatement.ThreeSum.SolvedInTime (4800698571997281331/2500000000000000000 : Rat) := by
  apply TernarySolverEndBridge.endStatement_of_solvers
  intro κ
  let P:=profile κ
  exact ⟨P.hybridProgram,P.hybridMain,P.hybridTime,P.hybridNeed,
    ternary_hybrid_solves P,P.hybrid_polyNeed,P.hybrid_time_target⟩

end ThreeSum
