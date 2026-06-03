#!/usr/bin/env python3
"""Build the MIT 18.06 (Gilbert Strang) fork — a video-first alternative
learning path for Linear Algebra, forked under World 1 / Vector Vale.

Source: MIT OpenCourseWare 18.06 Linear Algebra, Spring 2010 (CC BY-NC-SA 4.0).
We embed only lecture metadata + YouTube IDs (no large assets). Curated concept
cards & conceptual quizzes are authored here for correctness.

Output: backend/fork_content.json
"""
import json
import re
from pathlib import Path

BACKEND = Path(__file__).resolve().parent.parent / "backend"
LECTURES = json.loads((BACKEND / "mit1806_lectures.json").read_text())

XP = {"briefing": 20, "watch": 30, "concept": 25, "quiz": 40, "boss": 80}

# key -> {"objectives":[...], "watch_for":[...], "concepts":[(term,def)...], "quiz":[{q,correct,wrong,explain}]}
# Conceptual (non-numeric) to keep everything correct and recall-friendly.
C = {
 "1": {
   "objectives": ["See Ax=b as the row picture (intersecting lines/planes) and the column picture (combining vectors)",
                  "Understand a linear combination of columns"],
   "watch_for": ["How the column picture turns 'solve equations' into 'combine vectors'",
                 "When the columns can produce EVERY right-hand side b"],
   "concepts": [("Row picture", "Each equation is a line (2D) or plane (3D); the solution is where they all intersect."),
                ("Column picture", "Ax is a linear combination of A's columns; solving Ax=b asks which combination equals b.")],
   "quiz": [{"q": "In the column picture, what is Ax?",
             "correct": "A linear combination of the columns of A weighted by the entries of x",
             "wrong": ["The dot product of the rows of A", "The intersection point of the rows", "The determinant of A"],
             "explain": "Ax mixes the columns of A using x's entries — the heart of Strang's column picture."}],
 },
 "2": {
   "objectives": ["Perform elimination to reach upper-triangular form", "Read off pivots and spot a failure (zero pivot)"],
   "watch_for": ["What a pivot is", "What it means when a pivot is zero"],
   "concepts": [("Pivot", "The first nonzero entry in a row used to eliminate entries below it."),
                ("Elimination", "Systematically subtracting multiples of rows to reach upper-triangular form U.")],
   "quiz": [{"q": "Elimination fails (needs a row exchange) when…",
             "correct": "a pivot position contains a zero",
             "wrong": ["the matrix is square", "b has a zero entry", "the matrix is symmetric"],
             "explain": "A zero in the pivot position forces a row exchange (or signals singularity)."}],
 },
 "3": {
   "objectives": ["View matrix multiplication five ways", "Understand the inverse and when it exists"],
   "watch_for": ["Multiplication as combinations of columns AND of rows", "Why AB and BA differ"],
   "concepts": [("Inverse matrix", "A⁻¹ undoes A: A⁻¹A = I. It exists only when A is square and nonsingular."),
                ("Matrix multiplication", "Can be seen as rows·columns, column combinations, row combinations, or sum of rank-1 pieces.")],
   "quiz": [{"q": "A square matrix A has an inverse exactly when…",
             "correct": "it has no zero pivots (it is nonsingular)",
             "wrong": ["it is symmetric", "all entries are positive", "it is diagonal"],
             "explain": "Full set of nonzero pivots ⇔ invertible."}],
 },
 "4": {
   "objectives": ["Factor A = LU from elimination", "Understand L holds the elimination multipliers"],
   "watch_for": ["Where the multipliers go in L", "Why no row exchanges means A = LU"],
   "concepts": [("A = LU", "Elimination factors A into Lower-triangular L (the multipliers) times Upper-triangular U (the pivots)."),
                ("Permutation matrix P", "Identity with reordered rows; tracks row exchanges so PA = LU.")],
   "quiz": [{"q": "In A = LU, what does L contain?",
             "correct": "the multipliers used during elimination, with 1's on the diagonal",
             "wrong": ["the pivots", "the eigenvalues", "the right-hand side b"],
             "explain": "L records exactly the numbers you multiplied rows by to eliminate."}],
 },
 "5": {
   "objectives": ["Use permutations for row exchanges", "Define a vector space / subspace of Rⁿ"],
   "watch_for": ["Why P⁻¹ = Pᵀ", "The rules a subspace must satisfy"],
   "concepts": [("Transpose Aᵀ", "Flips rows and columns; (AB)ᵀ = BᵀAᵀ."),
                ("Subspace", "A set closed under addition and scalar multiplication, always containing the zero vector.")],
   "quiz": [{"q": "Which is REQUIRED for a set to be a subspace?",
             "correct": "It must contain the zero vector and be closed under + and scalar ×",
             "wrong": ["It must contain a basis of Rⁿ", "It must be finite", "It must be the column space of some A"],
             "explain": "Closed under linear combinations, and contains 0 — that's a subspace."}],
 },
 "6": {
   "objectives": ["Define column space and nullspace", "Connect solvability of Ax=b to the column space"],
   "watch_for": ["Column space = all reachable b", "Nullspace = all solutions to Ax=0"],
   "concepts": [("Column space C(A)", "All linear combinations of A's columns — exactly the b for which Ax=b is solvable."),
                ("Nullspace N(A)", "All solutions x to Ax=0; it is a subspace of Rⁿ.")],
   "quiz": [{"q": "Ax=b is solvable precisely when…",
             "correct": "b lies in the column space of A",
             "wrong": ["b lies in the nullspace of A", "A is square", "b is the zero vector"],
             "explain": "Reachable right-hand sides are exactly C(A)."}],
 },
 "7": {
   "objectives": ["Find pivot vs free variables", "Build special solutions to Ax=0"],
   "watch_for": ["How free variables generate the nullspace", "Rank = number of pivots"],
   "concepts": [("Free variable", "A variable with no pivot in its column; you set it freely to build nullspace solutions."),
                ("Rank", "The number of pivots — the true dimension of the row/column space.")],
   "quiz": [{"q": "The number of free variables of A equals…",
             "correct": "n minus the rank (number of columns minus pivots)",
             "wrong": ["the rank", "the number of rows", "the determinant"],
             "explain": "Free variables = n − r; each one gives a special nullspace solution."}],
 },
 "8": {
   "objectives": ["Describe ALL solutions to Ax=b", "Use reduced row echelon form R"],
   "watch_for": ["Particular + nullspace = complete solution", "When there are 0, 1, or ∞ solutions"],
   "concepts": [("Complete solution", "x_particular + (any nullspace vector); one particular solution plus all of N(A)."),
                ("Reduced form R", "rref(A): pivots are 1, with zeros above and below — reveals rank and free columns.")],
   "quiz": [{"q": "The complete solution to Ax=b is…",
             "correct": "one particular solution plus every vector in the nullspace",
             "wrong": ["only the particular solution", "only the nullspace", "the column space of A"],
             "explain": "x = x_p + x_n captures all solutions."}],
 },
 "9": {
   "objectives": ["Define independence, basis, dimension", "Relate basis size to rank"],
   "watch_for": ["Independence vs spanning", "Why every basis has the same size"],
   "concepts": [("Linear independence", "No vector is a combination of the others; only the trivial combination gives 0."),
                ("Basis", "An independent set that spans the space; its size is the dimension.")],
   "quiz": [{"q": "A basis of a subspace is…",
             "correct": "an independent set of vectors that spans the subspace",
             "wrong": ["any spanning set", "any independent set", "the largest set of vectors that fit"],
             "explain": "Independent AND spanning — both conditions define a basis."}],
 },
 "10": {
   "objectives": ["Name the four fundamental subspaces", "Know their dimensions and orthogonality"],
   "watch_for": ["Dimensions: r, r, n−r, m−r", "Which subspaces are orthogonal complements"],
   "concepts": [("Four subspaces", "Column space C(A) and nullspace N(A); row space C(Aᵀ) and left nullspace N(Aᵀ)."),
                ("Dimensions", "dim C(A)=dim C(Aᵀ)=r; dim N(A)=n−r; dim N(Aᵀ)=m−r.")],
   "quiz": [{"q": "The row space and column space of A always have…",
             "correct": "the same dimension, r (the rank)",
             "wrong": ["dimensions that differ by the nullity", "dimension n", "dimension m"],
             "explain": "Row rank = column rank = r — a cornerstone theorem."}],
   "boss": True,
 },
 "11": {
   "objectives": ["Treat matrices as a vector space", "Recognize rank-1 matrices"],
   "watch_for": ["Why every rank-1 matrix is a column times a row", "Bases of matrix spaces"],
   "concepts": [("Rank-1 matrix", "Can be written as a column vector times a row vector, uvᵀ — the building block of any matrix."),
                ("Matrix space", "Matrices form a vector space; e.g. 3×3 matrices have dimension 9.")],
   "quiz": [{"q": "Every rank-1 matrix can be written as…",
             "correct": "a column times a row, uvᵀ",
             "wrong": ["a sum of permutation matrices", "an orthogonal matrix", "a diagonal matrix"],
             "explain": "Rank 1 ⇔ outer product uvᵀ."}],
 },
 "12": {
   "objectives": ["Build incidence matrices from graphs", "Connect nullspace/loops to graph structure"],
   "watch_for": ["What the nullspace of an incidence matrix means", "Euler's formula appearing in linear algebra"],
   "concepts": [("Incidence matrix", "Rows = edges, columns = nodes; each row has −1 and +1 marking an edge's ends."),
                ("Graph nullspace", "The all-ones vector is in the nullspace — constant potentials cause no current.")],
   "quiz": [{"q": "The nullspace of a connected graph's incidence matrix is spanned by…",
             "correct": "the all-ones vector (constant potential)",
             "wrong": ["the zero vector only", "every edge vector", "the diagonal"],
             "explain": "Equal potentials everywhere ⇒ no flow ⇒ in the nullspace."}],
 },
 "13": {"checkpoint": "Unit 1 — Elimination, spaces & rank", "pool": ["2","3","6","7","8","9","10"]},
 "14": {
   "objectives": ["Define orthogonal vectors and subspaces", "Use the test xᵀy = 0"],
   "watch_for": ["Row space ⟂ nullspace", "Why orthogonal subspaces only meet at 0"],
   "concepts": [("Orthogonal vectors", "Two vectors are orthogonal when their dot product xᵀy = 0."),
                ("Orthogonal subspaces", "Every vector in one is orthogonal to every vector in the other; the row space ⟂ nullspace.")],
   "quiz": [{"q": "Vectors x and y are orthogonal when…",
             "correct": "their dot product xᵀy equals 0",
             "wrong": ["they are parallel", "they have equal length", "their sum is 0"],
             "explain": "Orthogonality ⇔ zero dot product."}],
 },
 "15": {
   "objectives": ["Project a vector onto a line/subspace", "Derive the projection formula"],
   "watch_for": ["The error e = b − p is orthogonal to the subspace", "Why we project: solve unsolvable systems"],
   "concepts": [("Projection", "The closest point p in a subspace to b; the error b−p is orthogonal to the subspace."),
                ("Projection onto a line", "p = (aᵀb / aᵀa) a — scale the direction a by the right amount.")],
   "quiz": [{"q": "When projecting b onto a subspace, the error vector b−p is…",
             "correct": "orthogonal to the subspace",
             "wrong": ["parallel to b", "the longest possible", "always zero"],
             "explain": "Projection minimizes distance ⇒ error ⟂ subspace."}],
 },
 "16": {
   "objectives": ["Build the projection matrix P", "Solve least squares via normal equations"],
   "watch_for": ["Why P² = P and Pᵀ = P", "The normal equations AᵀAx̂ = Aᵀb"],
   "concepts": [("Projection matrix", "P = A(AᵀA)⁻¹Aᵀ; it satisfies P² = P and Pᵀ = P."),
                ("Least squares", "Best-fit solution x̂ solving AᵀAx̂ = Aᵀb when Ax=b has no exact answer.")],
   "quiz": [{"q": "The least-squares 'normal equations' are…",
             "correct": "AᵀA x̂ = Aᵀb",
             "wrong": ["Ax = b", "AᵀA x = 0", "Ax̂ = Aᵀb"],
             "explain": "Projecting b onto C(A) yields AᵀAx̂ = Aᵀb."}],
   "boss": True,
 },
 "17": {
   "objectives": ["Define orthonormal/orthogonal matrices", "Run Gram-Schmidt to get Q"],
   "watch_for": ["Why QᵀQ = I", "How Gram-Schmidt removes overlaps"],
   "concepts": [("Orthogonal matrix Q", "Columns are orthonormal, so QᵀQ = I and Q preserves lengths."),
                ("Gram-Schmidt", "Turns independent vectors into orthonormal ones by subtracting projections, giving A = QR.")],
   "quiz": [{"q": "For an orthogonal matrix Q…",
             "correct": "QᵀQ = I and Q preserves vector lengths",
             "wrong": ["Q is always symmetric", "det Q = 0", "Q has a zero nullspace only if square"],
             "explain": "Orthonormal columns ⇒ QᵀQ = I; rotations/reflections preserve length."}],
 },
 "18": {
   "objectives": ["List the defining properties of determinants", "Use them to reason about singularity"],
   "watch_for": ["det I = 1, sign flips on row swap, linearity in each row", "det = 0 ⇔ singular"],
   "concepts": [("Determinant", "A single number; det A = 0 exactly when A is singular (no inverse)."),
                ("Determinant rules", "det I=1; a row swap flips the sign; det is linear in each row.")],
   "quiz": [{"q": "det A = 0 means…",
             "correct": "A is singular (not invertible)",
             "wrong": ["A is orthogonal", "A is symmetric", "A has full rank"],
             "explain": "Zero determinant ⇔ singular matrix."}],
 },
 "19": {
   "objectives": ["Compute determinants by cofactors", "See the big (permutation) formula"],
   "watch_for": ["Cofactor expansion along a row", "Why each term picks one entry per row and column"],
   "concepts": [("Cofactor", "Signed minor; expanding along a row/column builds the determinant recursively."),
                ("Big formula", "Sum over permutations of ± products, one entry from each row and column.")],
   "quiz": [{"q": "Cofactor expansion computes the determinant by…",
             "correct": "summing signed entries times the determinants of their minors",
             "wrong": ["multiplying the diagonal only", "adding the eigenvalues", "row-reducing to I"],
             "explain": "Each entry × signed minor, summed along a row or column."}],
 },
 "20": {
   "objectives": ["Apply Cramer's rule", "Connect determinant to volume"],
   "watch_for": ["A⁻¹ via cofactors/determinant", "|det| as the volume of a box"],
   "concepts": [("Cramer's rule", "Solves Ax=b using ratios of determinants (great theory, slow in practice)."),
                ("Determinant as volume", "|det A| is the volume of the parallelepiped spanned by A's columns.")],
   "quiz": [{"q": "|det A| geometrically equals…",
             "correct": "the volume of the box formed by A's column vectors",
             "wrong": ["the length of the longest column", "the trace of A", "the largest eigenvector"],
             "explain": "Determinant magnitude = signed volume scaling factor."}],
 },
 "21": {
   "objectives": ["Define eigenvalues and eigenvectors", "Use det(A−λI)=0"],
   "watch_for": ["Ax = λx keeps direction", "Trace = sum of λ, det = product of λ"],
   "concepts": [("Eigenvector", "A special direction x with Ax = λx — A only stretches it, never turns it."),
                ("Eigenvalue λ", "The stretch factor; found from det(A − λI) = 0.")],
   "quiz": [{"q": "x is an eigenvector of A when…",
             "correct": "Ax points along x, i.e. Ax = λx for some scalar λ",
             "wrong": ["Ax = 0 always", "Ax is orthogonal to x", "x is in the nullspace of Aᵀ"],
             "explain": "Eigenvectors keep their direction under A."}],
 },
 "22": {
   "objectives": ["Diagonalize A = SΛS⁻¹", "Compute powers Aᵏ easily"],
   "watch_for": ["Columns of S are eigenvectors", "Why Aᵏ = SΛᵏS⁻¹"],
   "concepts": [("Diagonalization", "A = SΛS⁻¹ where S holds eigenvectors and Λ holds eigenvalues — possible when eigenvectors are independent."),
                ("Powers of A", "Aᵏ = SΛᵏS⁻¹, so eigenvalues simply get raised to the k-th power.")],
   "quiz": [{"q": "In A = SΛS⁻¹, the columns of S are…",
             "correct": "the eigenvectors of A",
             "wrong": ["the pivots of A", "orthonormal always", "the rows of A"],
             "explain": "S's columns are eigenvectors; Λ is the diagonal of eigenvalues."}],
   "boss": True,
 },
 "23": {
   "objectives": ["Solve linear ODEs with eigenvalues", "Interpret the matrix exponential e^{At}"],
   "watch_for": ["Stability from the sign of eigenvalue real parts", "e^{At} via diagonalization"],
   "concepts": [("Matrix exponential", "e^{At} propagates a linear system; eigenvalues set growth/decay."),
                ("Stability", "Solutions decay when every eigenvalue has negative real part.")],
   "quiz": [{"q": "A linear system du/dt = Au is stable when…",
             "correct": "all eigenvalues of A have negative real part",
             "wrong": ["A is symmetric", "det A = 1", "A has a zero eigenvalue"],
             "explain": "Negative real parts ⇒ e^{λt} decays ⇒ stable."}],
 },
 "24": {
   "objectives": ["Recognize Markov matrices", "Find the steady state"],
   "watch_for": ["Columns sum to 1, λ=1 is an eigenvalue", "Steady state = eigenvector for λ=1"],
   "concepts": [("Markov matrix", "Nonnegative entries with columns summing to 1; always has eigenvalue λ = 1."),
                ("Steady state", "The eigenvector for λ=1 — the long-run distribution.")],
   "quiz": [{"q": "Every Markov matrix has an eigenvalue equal to…",
             "correct": "1, whose eigenvector is the steady state",
             "wrong": ["0", "−1", "its largest entry"],
             "explain": "Columns summing to 1 force λ=1."}],
 },
 "24b": {"checkpoint": "Unit 2 — Orthogonality, determinants & eigenvalues", "pool": ["14","15","16","17","18","21","22"]},
 "25": {
   "objectives": ["State the spectral theorem", "Define positive definiteness"],
   "watch_for": ["Symmetric ⇒ real eigenvalues & orthogonal eigenvectors", "Positive definite ⇔ all λ > 0"],
   "concepts": [("Symmetric matrix", "A = Aᵀ ⇒ real eigenvalues and orthonormal eigenvectors: A = QΛQᵀ."),
                ("Positive definite", "Symmetric with all eigenvalues positive (and xᵀAx > 0 for x≠0).")],
   "quiz": [{"q": "A symmetric matrix always has…",
             "correct": "real eigenvalues and orthogonal eigenvectors",
             "wrong": ["complex eigenvalues", "a zero determinant", "rank 1"],
             "explain": "The spectral theorem: symmetric ⇒ A = QΛQᵀ."}],
 },
 "26": {
   "objectives": ["Handle complex vectors/matrices", "Meet the Fourier matrix & FFT idea"],
   "watch_for": ["Hermitian replaces transpose for complex matrices", "Why the FFT is fast"],
   "concepts": [("Hermitian / conjugate transpose", "For complex matrices, use Aᴴ (conjugate transpose); Hermitian means A = Aᴴ."),
                ("Fourier matrix", "Orthogonal complex matrix whose structure lets the FFT factor it for huge speedups.")],
   "quiz": [{"q": "For complex matrices, the role of the transpose is played by…",
             "correct": "the conjugate transpose (Hermitian) Aᴴ",
             "wrong": ["the plain transpose Aᵀ", "the inverse A⁻¹", "the determinant"],
             "explain": "Complex inner products use the conjugate transpose."}],
 },
 "27": {
   "objectives": ["Test positive definiteness multiple ways", "Link to minima of xᵀAx"],
   "watch_for": ["Pivots, determinants, eigenvalues, xᵀAx tests", "Why PD ⇒ a true minimum"],
   "concepts": [("PD tests", "Positive definite ⇔ all eigenvalues > 0 ⇔ all pivots > 0 ⇔ all leading determinants > 0."),
                ("Energy xᵀAx", "Positive definiteness means xᵀAx > 0, giving a bowl with a unique minimum.")],
   "quiz": [{"q": "Which is a valid test for positive definiteness?",
             "correct": "All pivots (equivalently all eigenvalues) are positive",
             "wrong": ["The matrix is triangular", "The trace is zero", "Some eigenvalue is negative"],
             "explain": "PD ⇔ positive pivots ⇔ positive eigenvalues ⇔ positive leading minors."}],
 },
 "28": {
   "objectives": ["Define matrix similarity", "Meet Jordan form for non-diagonalizable A"],
   "watch_for": ["Similar matrices share eigenvalues", "When diagonalization fails"],
   "concepts": [("Similar matrices", "B = M⁻¹AM; similar matrices have the same eigenvalues."),
                ("Jordan form", "The closest-to-diagonal form when A lacks enough independent eigenvectors.")],
   "quiz": [{"q": "Similar matrices A and M⁻¹AM always share…",
             "correct": "the same eigenvalues",
             "wrong": ["the same eigenvectors", "the same entries", "the same column space"],
             "explain": "Similarity preserves eigenvalues (the characteristic polynomial)."}],
 },
 "29": {
   "objectives": ["State the SVD A = UΣVᵀ", "Know it exists for ANY matrix"],
   "watch_for": ["U,V orthogonal; Σ diagonal of singular values", "SVD connects the four subspaces"],
   "concepts": [("SVD", "A = UΣVᵀ: orthogonal U and V, diagonal Σ of singular values — works for every matrix."),
                ("Singular values", "Nonnegative diagonal entries of Σ; squares are eigenvalues of AᵀA.")],
   "quiz": [{"q": "The singular value decomposition A = UΣVᵀ exists for…",
             "correct": "any matrix whatsoever (any shape, any rank)",
             "wrong": ["only square matrices", "only symmetric matrices", "only invertible matrices"],
             "explain": "Strang: the SVD is the final, best factorization — it always exists."}],
   "boss": True,
 },
 "30": {
   "objectives": ["See linear transformations behind matrices", "Choose bases to get the matrix"],
   "watch_for": ["A transformation + bases ⇒ a matrix", "Why the matrix depends on the basis"],
   "concepts": [("Linear transformation", "A rule T with T(x+y)=T(x)+T(y) and T(cx)=cT(x); matrices represent them once you fix bases."),
                ("Matrix of a transformation", "Columns are the images of the basis vectors written in the output basis.")],
   "quiz": [{"q": "A matrix represents a linear transformation only after you…",
             "correct": "choose input and output bases",
             "wrong": ["invert the matrix", "make it symmetric", "compute its determinant"],
             "explain": "The same transformation has different matrices in different bases."}],
 },
 "31": {
   "objectives": ["Change basis with B = M⁻¹AM-style maps", "See compression as a basis choice"],
   "watch_for": ["Why a good basis makes data sparse", "Connection to SVD compression"],
   "concepts": [("Change of basis", "Re-express vectors/operators in a new basis via an invertible change-of-basis matrix."),
                ("Image compression", "Pick a basis where most coefficients are tiny, then keep only the big ones.")],
   "quiz": [{"q": "Image compression works by…",
             "correct": "choosing a basis where most coefficients are negligible and discarding them",
             "wrong": ["deleting random pixels", "inverting the image matrix", "making the matrix symmetric"],
             "explain": "A smart basis concentrates information into a few coefficients."}],
 },
 "32": {"checkpoint": "Unit 3 — Positive definite, SVD & transformations", "pool": ["25","27","28","29","30"]},
 "33": {
   "objectives": ["Distinguish left/right inverses", "Define the pseudoinverse"],
   "watch_for": ["Full column rank ⇒ left inverse", "Pseudoinverse handles any shape/rank"],
   "concepts": [("One-sided inverses", "Full column rank gives a left inverse; full row rank gives a right inverse."),
                ("Pseudoinverse A⁺", "The best inverse for any matrix; maps b to the least-squares minimum-norm solution.")],
   "quiz": [{"q": "The pseudoinverse A⁺ is useful because it…",
             "correct": "gives the best (least-squares, minimum-norm) solution for ANY matrix",
             "wrong": ["only exists for square matrices", "equals the transpose", "requires positive definiteness"],
             "explain": "A⁺ extends 'inverse' to rectangular/rank-deficient matrices."}],
 },
 "34": {"checkpoint": "Final Review — the whole course", "pool": ["1","6","10","16","21","25","29"]},
}


def make_quiz_questions(entries, fork_concepts, rng_seed=0):
    import hashlib, random
    qs = []
    for e in entries:
        opts = e["wrong"] + [e["correct"]]
        h = int(hashlib.sha256((e["q"]).encode()).hexdigest(), 16)
        random.Random(h).shuffle(opts)
        qs.append({"q": e["q"], "options": opts, "answer": opts.index(e["correct"]),
                   "explain": e["explain"]})
    return qs


def build():
    fork_levels = []
    # gather all curated quiz entries by key for checkpoint pools
    quiz_by_key = {k: v.get("quiz", []) for k, v in C.items() if v.get("quiz")}

    for lec in LECTURES:
        key = f"{lec['num']}{lec['suffix']}"
        cur = C.get(key, {})
        lid = f"mit1806-{lec['num']:02d}{lec['suffix']}"
        missions = []

        # 1. Briefing
        missions.append({
            "id": f"{lid}::briefing", "type": "briefing", "title": "Lecture Briefing",
            "objective": "Get the big idea before you watch Strang.",
            "estimated_minutes": 2, "xp_reward": XP["briefing"],
            "payload": {"tagline": lec["title"], "why_it_matters": lec["summary"],
                        "objectives": cur.get("objectives", []), "languages": "MIT 18.06 · Gilbert Strang"},
        })
        # 2. Watch (the real Strang video)
        if lec.get("youtube_id"):
            missions.append({
                "id": f"{lid}::watch", "type": "watch", "title": "Watch the Lecture",
                "objective": "Watch Prof. Strang teach it (the best part).",
                "estimated_minutes": 7, "xp_reward": XP["watch"],
                "payload": {"youtube_id": lec["youtube_id"], "title": lec["full_title"],
                            "watch_for": cur.get("watch_for", ["Follow Strang's reasoning end to end."])},
            })

        if cur.get("checkpoint"):
            # Checkpoint: boss pulling from a pool of earlier lectures
            pool_q = []
            for pk in cur.get("pool", []):
                pool_q.extend(quiz_by_key.get(pk, []))
            qs = make_quiz_questions(pool_q, None)
            if qs:
                missions.append({
                    "id": f"{lid}::boss", "type": "boss", "title": f"Checkpoint: {cur['checkpoint']}",
                    "objective": "Prove the unit stuck. Retry freely — no penalty.",
                    "estimated_minutes": 6, "xp_reward": XP["boss"],
                    "payload": {"questions": qs, "pass_threshold": max(1, int(len(qs) * 0.6)),
                                "recap": [cur["checkpoint"]]},
                })
            tagline = cur["checkpoint"]
            review_terms = []
        else:
            # 3. Concept cards
            concepts = cur.get("concepts", [])
            if concepts:
                missions.append({
                    "id": f"{lid}::concept", "type": "concept", "title": "Concept Cards",
                    "objective": "Tap each card. Recall the idea, then confirm.",
                    "estimated_minutes": 3, "xp_reward": XP["concept"],
                    "payload": {"front_label": "Recall", "reveal_suffix": "— explained",
                                "cards": [{"term": t, "front": f"What is {t.lower()}?", "back": d} for t, d in concepts]},
                })
            # 4. Quiz
            qs = make_quiz_questions(cur.get("quiz", []), None)
            if qs:
                missions.append({
                    "id": f"{lid}::quiz", "type": "quiz", "title": "Comprehension Check",
                    "objective": "One quick check. Immediate feedback, retry freely.",
                    "estimated_minutes": 3, "xp_reward": XP["quiz"],
                    "payload": {"questions": qs},
                })
            tagline = cur.get("objectives", [lec["title"]])[0] if cur.get("objectives") else lec["title"]
            review_terms = [{"term": t, "myth": "", "reality": d} for t, d in cur.get("concepts", [])]

        fork_levels.append({
            "id": lid, "is_fork": True, "fork_id": "mit-1806",
            "world_id": 1, "order": lec["num"] * 10 + (1 if lec["suffix"] else 0),
            "title": f"L{lec['num']}{lec['suffix'].upper()} · {lec['title']}",
            "tagline": tagline, "type": "Video Lecture",
            "estimated_minutes": sum(m["estimated_minutes"] for m in missions),
            "objectives": cur.get("objectives", []),
            "source_path": "MIT OCW 18.06 (CC BY-NC-SA 4.0)",
            "missions": missions,
            "review_terms": review_terms,
            "youtube_id": lec.get("youtube_id"),
        })

    fork = {
        "id": "mit-1806",
        "world_id": 1,
        "anchor_level_id": "01-01-linear-algebra-intuition",
        "name": "MIT 18.06 — Strang's Linear Algebra",
        "short": "Video-first fork",
        "source": "MIT OpenCourseWare · Prof. Gilbert Strang (CC BY-NC-SA 4.0)",
        "tagline": "Widely called the best linear algebra course in the world. Learn it the way MIT does — watch, then lock it in.",
        "skill": "product-thinking",
        "level_count": len(fork_levels),
        "levels": fork_levels,
    }
    out = {"version": 1, "forks": [fork]}
    (BACKEND / "fork_content.json").write_text(json.dumps(out, ensure_ascii=False, indent=2))
    print(f"Wrote fork_content.json — {len(fork_levels)} lecture levels")
    tot_missions = sum(len(l["missions"]) for l in fork_levels)
    print(f"Total fork missions: {tot_missions}")


if __name__ == "__main__":
    build()
