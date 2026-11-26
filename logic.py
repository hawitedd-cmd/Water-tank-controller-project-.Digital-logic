# ---------- basic gates ----------
def NOT(a):
    return 0 if a else 1


def AND(a, b):
    return 1 if (a and b) else 0


def OR(a, b):
    return 1 if (a or b) else 0


# ---------- SR latch (memory) built from gates ----------
# Remembers that the pump was started when the tank was low, so the pump keeps
# running until the tank is FULL (this is called hysteresis).
# Reset has priority over Set (safe: never keep pumping a full tank).
def sr_latch(set_, reset, q_prev):
    # Q_next = (S OR Q) AND NOT R
    return AND(OR(set_, q_prev), NOT(reset))


# ---------- the controller ----------
def controller(L, H, E, q_prev):
    """One evaluation of the controller. Returns (outputs dict, new latch state)."""
    S = NOT(L)                    # Set   : tank is low
    R = OR(H, NOT(E))             # Reset : tank full OR system disabled
    Q = sr_latch(S, R, q_prev)

    fault = AND(H, NOT(L))        # high probe wet but low probe dry -> broken sensor
    pump = AND(Q, NOT(fault))     # never pump when a fault is detected

    outputs = {
        "PUMP": pump,
        "FAULT": fault,
        "LOW": NOT(L),
        "FULL": H,
    }
    return outputs, Q


def truth_table():
    """Combinational view (assumes the latch was OFF before) for the report."""
    rows = []
    for E in (0, 1):
        for H in (0, 1):
            for L in (0, 1):
                out, _ = controller(L, H, E, 0)
                rows.append((E, H, L, out["PUMP"], out["FAULT"], out["LOW"], out["FULL"]))
    return rows


if __name__ == "__main__":
    print("E H L | PUMP FAULT LOW FULL")
    for r in truth_table():
        print(f"{r[0]} {r[1]} {r[2]} |  {r[3]}     {r[4]}     {r[5]}    {r[6]}")
