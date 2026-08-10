from models.ai_task import AITask




def test_ai_task():


    task = AITask(

        article_id=1,

        task_type="analysis",

        priority=10

    )



    assert task.article_id == 1


    assert task.task_type == "analysis"


    assert task.is_waiting is True



    task.start()


    assert task.is_running is True



    task.complete()


    assert task.is_finished is True



    print(

        "AITask Model OK"

    )





if __name__ == "__main__":

    test_ai_task()