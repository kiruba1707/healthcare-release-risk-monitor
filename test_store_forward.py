from core.store_forward import (
    store_event,
    get_buffered_events,
    forward_events
)


print("=" * 60)
print("STORE-AND-FORWARD TEST")
print("=" * 60)


# Simulated monitoring event
event = {
    "release_id": "RTEST01",
    "hospital_id": "H001",
    "version": "v3.0",
    "error_rate": 7.2,
    "latency_ms": 650
}


# --------------------------------------------------
# STEP 1 — Network unavailable
# --------------------------------------------------

print("\n[1] Network unavailable")

result = forward_events(
    server_available=False
)

print(result)


# --------------------------------------------------
# STEP 2 — Store event locally
# --------------------------------------------------

print("\n[2] Storing event locally")

store_event(event)

print("Event stored successfully.")


# --------------------------------------------------
# STEP 3 — Check local buffer
# --------------------------------------------------

buffer = get_buffered_events()

print("\n[3] Buffered events:")
print(len(buffer))

for item in buffer:
    print(item)


# --------------------------------------------------
# STEP 4 — Network restored
# --------------------------------------------------

print("\n[4] Network restored")

result = forward_events(
    server_available=True
)

print(result)


# --------------------------------------------------
# STEP 5 — Verify buffer
# --------------------------------------------------

buffer = get_buffered_events()

print("\n[5] Remaining buffered events:")
print(len(buffer))


print("\nStore-and-forward test completed.")