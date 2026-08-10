"""
models/ai_task.py

AutoSearch V4

AI Task Model


用途:

    管理 AI 非同步分析任務


Database:

    ai_tasks


V4 Phase 1.1


"""


from datetime import datetime





class AITask:




    def __init__(

        self,


        article_id=None,


        task_type="analysis",


        status="WAITING",


        priority=0,


        retry_count=0,


        created_time=None,


        finished_time=None


    ):



        # ==========================
        # Database ID
        # ==========================


        self.id = None



        # ==========================
        # Article Relation
        # ==========================


        self.article_id = article_id



        # ==========================
        # Task Information
        # ==========================


        self.task_type = task_type



        self.status = status



        self.priority = priority



        self.retry_count = retry_count



        # ==========================
        # Time
        # ==========================


        self.created_time = (

            created_time

            if created_time

            else datetime.now()

        )



        self.finished_time = finished_time





    # ==================================
    # Task Property
    # ==================================



    @property
    def is_waiting(self):


        return (

            self.status

            ==

            "WAITING"

        )





    @property
    def is_running(self):


        return (

            self.status

            ==

            "RUNNING"

        )





    @property
    def is_finished(self):


        return (

            self.status

            ==

            "DONE"

        )





    @property
    def can_retry(self):


        return (

            self.retry_count

            <

            3

        )





    # ==================================
    # Task Control
    # ==================================



    def start(self):


        self.status = "RUNNING"





    def complete(self):


        self.status = "DONE"


        self.finished_time = datetime.now()





    def fail(self):


        self.status = "FAILED"


        self.retry_count += 1






    # ==================================
    # Dictionary
    # ==================================



    def to_dict(self):


        return {


            "id":

            self.id,



            "article_id":

            self.article_id,



            "task_type":

            self.task_type,



            "status":

            self.status,



            "priority":

            self.priority,



            "retry_count":

            self.retry_count,



            "created_time":

            self.created_time,



            "finished_time":

            self.finished_time


        }





    def __repr__(self):


        return (


            f"AITask("

            f"article_id={self.article_id}, "

            f"type={self.task_type}, "

            f"status={self.status}"

            ")"


        )