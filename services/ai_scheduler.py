"""
services/ai_scheduler.py

AutoSearch V4

P2.2.5 Step 6

AI Scheduler / Worker Runner


Flow:

Timer
 |
 v
AI Scheduler
 |
 v
AI Worker
 |
 v
AI Analysis Pipeline


功能:

1. Background AI Worker Runner
2. Periodic Task Processing
3. Single Run Mode
4. Worker Lock Protection

"""


import time
import threading


from ai.worker import AIWorker

from utils.logger import logger



class AIScheduler:
    """
    AI Background Scheduler

    負責:

    - 啟動 Worker
    - 定期執行 AI Task
    - 管理生命週期


    不負責:

    - AI Analysis
    - Database
    - Task Logic

    """


    def __init__(
        self,
        interval=30
    ):


        self.interval = interval


        self.worker = AIWorker()


        self.running = False


        self.thread = None


        self.lock = threading.Lock()



    # ==================================
    #
    # Run Once
    #
    # ==================================

    def run_once(self):


        if not self.lock.acquire(
            blocking=False
        ):

            logger.warning(
                "AI Scheduler already running"
            )

            return 0



        try:


            logger.info(
                "AI Scheduler executing worker"
            )


            result = self.worker.run_once()



            logger.info(
                f"AI Scheduler completed count={result}"
            )


            return result



        except Exception as e:


            logger.exception(
                f"AI Scheduler failed: {e}"
            )


            return 0



        finally:


            self.lock.release()





    # ==================================
    #
    # Background Loop
    #
    # ==================================

    def _loop(self):


        logger.info(
            "AI Scheduler started"
        )



        while self.running:


            self.run_once()



            time.sleep(
                self.interval
            )



        logger.info(
            "AI Scheduler stopped"
        )






    # ==================================
    #
    # Start
    #
    # ==================================

    def start(self):


        if self.running:


            logger.warning(
                "AI Scheduler already started"
            )


            return



        self.running = True



        self.thread = threading.Thread(

            target=self._loop,

            daemon=True

        )



        self.thread.start()



        logger.info(
            "AI Scheduler thread started"
        )






    # ==================================
    #
    # Stop
    #
    # ==================================

    def stop(self):


        logger.info(
            "Stopping AI Scheduler"
        )


        self.running = False



        if self.thread:


            self.thread.join(
                timeout=5
            )



        logger.info(
            "AI Scheduler stopped"

        )






# ==================================
#
# Standalone Runner
#
# ==================================


if __name__ == "__main__":


    scheduler = AIScheduler(
        interval=30
    )


    try:


        scheduler.start()



        while True:

            time.sleep(1)



    except KeyboardInterrupt:


        scheduler.stop()