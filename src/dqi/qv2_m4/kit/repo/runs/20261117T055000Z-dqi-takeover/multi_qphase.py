# SPDX-License-Identifier: Apache-2.0
# Uses Syed Asad Ali's Apache-2.0 paired_phase62 primitives; new arbitrary-target batching.
"""Pay sum_j <mask_j, target_j / factor> with one variable-numerator quotient phase.
Classical first-nonzero-mask selection borrows one target reversibly as the numerator.
The factor, all targets and masks are restored. Zero masks take the identity branch.
"""
from paired_phase62 import classical_word,classical_inverse,classical_scale,trace_columns
from quantum_reciprocal import xor_linear
from tower_inverse import xor_product
from quotient_phase62 import phase_inverse_trace_twelve

def emit(builder,factor,targets):
 polynomial,_=trace_columns();mus=[]
 for word,mask in targets:
  assert len(word)==len(mask)==len(factor)==12
  mu=classical_word(builder);xor_linear(builder,mask,mu,polynomial);mus.append(mu)
 seen=classical_word(builder,1)
 for i,((x,_),mu) in enumerate(zip(targets,mus)):
  has=classical_word(builder,1);builder.bit_store(has[0],True,control=mu)
  pick=classical_word(builder,1)
  builder.x(seen);builder.push_condition(has[0]);builder.push_condition(seen[0])
  builder.bit_store(pick[0],True)
  builder.pop_condition();builder.pop_condition();builder.x(seen);builder.cx(pick,seen)
  builder.push_condition(pick[0])
  reciprocal,owned=classical_inverse(builder,mu)
  classical_scale(builder,x,mu,reciprocal)
  for j,((y,_),nu) in enumerate(zip(targets,mus)):
   if j!=i:xor_product(builder,y,nu,x)
  phase_inverse_trace_twelve(builder,factor,x)
  for j,((y,_),nu) in reversed(list(enumerate(zip(targets,mus)))):
   if j!=i:xor_product(builder,y,nu,x)
  classical_scale(builder,x,reciprocal,mu)
  for word in owned:builder.free(word)
  builder.pop_condition();builder.free(has);builder.free(pick)
 for mu in mus:builder.free(mu)
 builder.free(seen)
