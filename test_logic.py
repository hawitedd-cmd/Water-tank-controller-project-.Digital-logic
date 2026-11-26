
from logic import controller, truth_table

# 1. Truth table (latch initially OFF)
expected = {
    # (E, H, L): (PUMP, FAULT)
    (0, 0, 0): (0, 0), (0, 0, 1): (0, 0), (0, 1, 0): (0, 1), (0, 1, 1): (0, 0),
    (1, 0, 0): (1, 0), (1, 0, 1): (0, 0), (1, 1, 0): (0, 1), (1, 1, 1): (0, 0),
}
for E, H, L, pump, fault, low, full in truth_table():
    assert (pump, fault) == expected[(E, H, L)], (E, H, L, pump, fault)
print("Truth table OK")

# 2. Hysteresis: empty -> pump on, stays on in the middle, off when full
q = 0
out, q = controller(L=0, H=0, E=1, q_prev=q);  assert out["PUMP"] == 1   # empty
out, q = controller(L=1, H=0, E=1, q_prev=q);  assert out["PUMP"] == 1   # filling
out, q = controller(L=1, H=1, E=1, q_prev=q);  assert out["PUMP"] == 0   # full
out, q = controller(L=1, H=0, E=1, q_prev=q);  assert out["PUMP"] == 0   # draining
print("Hysteresis OK")

# 3. Disable switch stops the pump even when tank is empty
out, q = controller(L=0, H=0, E=0, q_prev=0);  assert out["PUMP"] == 0
print("Enable switch OK")

# 4. Fault: high wet but low dry
out, q = controller(L=0, H=1, E=1, q_prev=0);  assert out["FAULT"] == 1 and out["PUMP"] == 0
print("Fault detection OK")

print("ALL TESTS PASSED")
