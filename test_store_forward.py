import core.store_forward as store_forward


def test_store_event():
    store_forward._save_buffer([])

    event = {
        "release_id": "R001",
        "hospital_id": "H001",
        "decision": "BLOCK"
    }

    result = store_forward.store_event(event)

    assert result is True

    buffered = store_forward.get_buffered_events()

    assert len(buffered) == 1
    assert buffered[0]["release_id"] == "R001"
    assert "stored_at" in buffered[0]

    store_forward._save_buffer([])


def test_forward_when_server_offline():
    store_forward._save_buffer([])

    store_forward.store_event({
        "release_id": "R002",
        "hospital_id": "H002",
        "decision": "HOLD"
    })

    result = store_forward.forward_events(server_available=False)

    assert result["status"] == "OFFLINE"
    assert result["forwarded"] == 0
    assert result["remaining"] == 1

    store_forward._save_buffer([])


def test_forward_when_server_available():
    store_forward._save_buffer([])

    store_forward.store_event({
        "release_id": "R003",
        "hospital_id": "H003",
        "decision": "SAFE"
    })

    result = store_forward.forward_events(server_available=True)

    assert result["status"] == "FORWARDED"
    assert result["forwarded"] == 1
    assert result["remaining"] == 0

    assert store_forward.get_buffered_events() == []
