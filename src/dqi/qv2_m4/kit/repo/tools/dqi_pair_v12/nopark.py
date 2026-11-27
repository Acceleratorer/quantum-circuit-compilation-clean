# SPDX-License-Identifier: Apache-2.0
"""Lane dqi_v9: measurement patch for Syed Asad Ali's v12 conversion (Apache-2.0). The gauge flag is never lent
(one more wire, 890 qubits): GaugeCarrier.park/unpark keep only their bookkeeping (no gates), and a parked scale phase
becomes the plain bilinear phase on the (unparked) unit, 0 Toffolis."""
import sys


def apply():
    import gauge_park_lender as GL
    import parked_scale_phase as PSP
    from tower_inverse import kernel, phase_product
    C = GL.GaugeCarrier

    def park(self, unit, label=''):
        assert self.anchor is None and self.b.idle and not self.b.enabled
        assert len(unit) == 12 and not set(unit) & set(self.other) and self.flag not in set(unit)
        self.anchor = unit; self.mask = 'virtual'; self.parks += 1; self.events.append(('park', label))

    def unpark(self, label=''):
        assert self.anchor is not None and self.b.idle and not self.b.enabled
        self.anchor = None; self.mask = None; self.unparks += 1; self.events.append(('unpark', label))

    def repay(builder, carrier, target, mask, label=''):
        assert carrier.anchor is not None and len(target) == len(carrier.anchor) == len(mask) == 12
        phase_product(builder, target, carrier.anchor, mask, kernel(12))
        builder.free(mask)
        carrier.parked_phase_payments = getattr(carrier, 'parked_phase_payments', 0) + 1
        carrier.events.append(('pay_parked_scale', label))

    C.park, C.unpark, PSP.repay_parked_scale = park, unpark, repay
    for name, mod in list(sys.modules.items()):
        if mod is not None and getattr(mod, 'repay_parked_scale', None) is not None and mod is not PSP \
                and name not in ('masked_parked_scale_phase',):
            print('NOPARK: also bound in', name, flush=True)
