"""
tests/test_ai_scheduler.py

AutoSearch V4

P2.2.5 Step 6

Test:

AI Scheduler / Worker Runner

"""


from unittest.mock import MagicMock, patch


from services.ai_scheduler import AIScheduler




# ==================================
# Test Run Once Success
# ==================================

def test_ai_scheduler_run_once():


    scheduler = AIScheduler(
        interval=10
    )


    scheduler.worker = MagicMock()


    scheduler.worker.run_once.return_value = 5



    result = scheduler.run_once()



    assert result == 5


    scheduler.worker.run_once.assert_called_once()





# ==================================
# Test Lock Protection
# ==================================

def test_ai_scheduler_lock():


    scheduler = AIScheduler()



    scheduler.worker = MagicMock()


    scheduler.worker.run_once.return_value = 1



    # manually acquire lock

    scheduler.lock.acquire()



    try:


        result = scheduler.run_once()



        assert result == 0



    finally:


        scheduler.lock.release()





# ==================================
# Test Start Stop
# ==================================

@patch(
    "services.ai_scheduler.time.sleep"
)
def test_ai_scheduler_start_stop(
    mock_sleep
):


    scheduler = AIScheduler(
        interval=1
    )


    scheduler.worker = MagicMock()


    scheduler.worker.run_once.return_value = 0



    scheduler.start()



    assert scheduler.running is True



    scheduler.stop()



    assert scheduler.running is False