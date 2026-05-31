• Under a unimodular basis change the K‑matrix and charge vector transform as  
  \(K' = W^{\!T} K W\) and \(t' = W^{\!T} t\).  
  Because \(W\) is invertible over the integers, \((K')^{-1} = W^{-1} K^{-1} (W^{\!T})^{-1}\). Substituting into the transformed filling fraction gives  

  \[
  \nu' = t'^{\!T}(K')^{-1}t'
        = (W^{\!T}t)^{\!T} W^{-1} K^{-1} (W^{\!T})^{-1} W^{\!T} t
        = t^{\!T} W W^{-1} K^{-1} (W^{\!T})^{-1} W^{\!T} t
        = t^{\!T} K^{-1} t = \nu .
  \]

  For the given instance \(K=[[3,1],[1,3]]\), \(t=[1,1]\), \(W=[[1,1],[0,1]]\) we have  

  * \(K' = W^{\!T} K W = [[3,4],[4,8]]\),  
  * \(t' = W^{\!T} t = [1,2]\),  
  * \(\det K = \det K' = 8\), so  
    \(K^{-1} = \tfrac{1}{8}[[3,-1],[-1,3]]\) and \((K')^{-1} = \tfrac{1}{8}[[8,-4],[-4,3]]\).  

  Evaluating,
  \[
  \nu = [1,1]\,K^{-1}[1,1] = \tfrac12,\qquad
  \nu' = [1,2]\,(K')^{-1}[1,2] = \tfrac12 .
  \]

  Thus \(\nu'=\nu\) and the filling fraction is invariant.

  ```json
  {
    "task_id": "wen-kmatrix-basis-invariance",
    "derivation_claim": "nu_prime = nu",
    "steps": [
      {
        "id": "S1",
        "statement": "Apply the basis transform to the instance: K_prime = W^T K W = [[3,4],[4,8]].",
        "rule": "matrix_basis_transform",
        "depends_on": []
      },
      {
        "id": "S2",
        "statement": "Apply the charge transform to the instance: t_prime = W^T t = [1,2].",
        "rule": "matrix_basis_transform",
        "depends_on": []
      },
      {
        "id": "S3",
        "statement": "Numeric evaluation: det(K)=8, K^{-1} = (1/8)[[3,-1],[-1,3]], so nu = t^T K^{-1} t = 1/2.",
        "rule": "numeric_instance_check",
        "depends_on": []
      },
      {
        "id": "S4",
        "statement": "Numeric evaluation: det(K_prime)=8, (K_prime)^{-1} = (1/8)[[8,-4],[-4,3]], so nu_prime = t_prime^T (K_prime)^{-1} t_prime = 1/2.",
        "rule": "numeric_instance_check",
        "depends_on": ["S1", "S2"]
      },
      {
        "id": "S5",
        "statement": "Since both nu and nu_prime equal 1/2, the filling fraction is invariant under this basis change.",
        "rule": "scalar_equality",
        "depends_on": ["S3", "S4"]
      }
    ],
    "K_prime": [[3, 4], [4, 8]],
    "t_prime": [1, 2],
    "nu": "1/2",
    "nu_prime": "1/2",
    "invariant": true,
    "no_novelty_claim": true,
    "source_excerpt_used": "wen-kmatrix-basis-transform-minimal"
  }
  ```

