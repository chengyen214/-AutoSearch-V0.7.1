"""
knowledge_persistence.py

AutoSearch V4

P1.6 Step 4

Knowledge Persistence Pipeline


功能:

1. 接收 Knowledge Object

2. 檢查 Knowledge 是否存在

3. Insert / Update

4. 儲存 knowledge_archive


Flow:


Knowledge

    |

    v

KnowledgePersistence

    |

    v

KnowledgeRepository

    |

    v

knowledge_archive

"""


from database.knowledge_repository import (
    KnowledgeRepository
)


from utils.logger import logger





class KnowledgePersistence:

    """
    Knowledge Persistence Layer

    負責 Knowledge 儲存

    """



    def __init__(self):


        self.repository = KnowledgeRepository()





    # ==================================
    # Save Knowledge
    # ==================================


    def save(

        self,

        knowledge

    ):


        """
        儲存 Knowledge


        Insert:

            不存在


        Update:

            已存在


        """


        try:


            exists = self.repository.exists(

                knowledge.article_id

            )



            if exists:



                self.repository.update(

                    knowledge.article_id,

                    knowledge

                )



                logger.info(

                    f"Knowledge updated: article_id={knowledge.article_id}"

                )



                return self.repository.get_by_article_id(

                    knowledge.article_id

                )





            else:



                result = self.repository.insert(

                    knowledge

                )



                logger.info(

                    f"Knowledge inserted: article_id={knowledge.article_id}"

                )


                return result





        except Exception as e:


            logger.error(

                f"Knowledge persistence failed: {e}"

            )


            raise