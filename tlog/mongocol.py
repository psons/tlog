from pymongo import MongoClient

# mongdb Endeavor collection module

import pprint
from endeavor import Endeavor
def upsert_endeavor(an_endeavor: Endeavor):
    client = MongoClient('localhost', 27017)
    db = client['tlog']         # tlog is the db
    endeavors = db['endeavors'] # endeavors is the collection

    # endeavor_id = endeavors.insert_one(an_endeavor.as_encodable()).inserted_id
    endeavor_id = endeavors.update_one(
        {'_id': an_endeavor.eid},
        {"$set": an_endeavor.as_encodable()}, upsert=True).upserted_id

    print(f"Mongo! endeavor _id: {endeavor_id} inserted into {endeavors}")

def list_endeavors():
    client = MongoClient('localhost', 27017)
    db = client['tlog']         # tlog is the db
    endeavors = db['endeavors'] # endeavors is the collection
    for endeavor in endeavors.find():
        pprint.pprint(endeavor)



if __name__ == '__main__':
    #client = MongoClient();
    client = MongoClient('localhost', 27017)
    db = client['tlog'] # tlog is the db
    # endeavors = db.endeavors
    endeavors = db['endeavors']

    # endeavor = {
    #     "_id": "c21f969b5f",
    #     "name": "default",
    #     "maxStories": 3,
    #     "eid": "c21f969b5f",
    #     "story_list": [
    #         {
    #             "maxTasks": " 3",
    #             "name": "new task story",
    #             "sid": "c21f969b5f.c9ec52c702",
    #             "taskList": [
    #                 {
    #                     "status": "in_progress",
    #                     "title": "live in the moment",
    #                     "detail": "",
    #                     "tid": "c21f969b5f.c9ec52c702.0eeac89fb5"
    #                 },
    #                 {
    #                     "status": "do",
    #                     "title": "think about the future",
    #                     "detail": "",
    #                     "tid": "c21f969b5f.c9ec52c702.d06267f230"
    #                 },
    #                 {
    #                     "status": "do",
    #                     "title": "another task",
    #                     "detail": "",
    #                     "tid": "c21f969b5f.c9ec52c702.e34beb1074"
    #                 },
    #                 {
    #                     "status": "do",
    #                     "title": "yet another task",
    #                     "detail": "",
    #                     "tid": "c21f969b5f.c9ec52c702.5103dd140c"
    #                 },
    #                 {
    #                     "status": "do",
    #                     "title": "yet another nother task",
    #                     "detail": "",
    #                     "tid": "c21f969b5f.c9ec52c702.92292d0f87"
    #                 }
    #             ]
    #         }
    #     ]
    # }
    #
    # endeavor1 = {
    #     "_id": "c21f969b5f",
    #     "name": "default",
    #     "maxStories": 3,
    #     "eid": "c21f969b5f",
    #     "story_list": [
    #         {
    #             "maxTasks": " 3",
    #             "name": "new task story",
    #             "sid": "c21f969b5f.c9ec52c702",
    #             "taskList": [
    #                 {
    #                     "status": "in_progress",
    #                     "title": "updated task was: live in the moment",
    #                     "detail": "",
    #                     "tid": "c21f969b5f.c9ec52c702.0eeac89fb5"
    #                 },
    #                 {
    #                     "status": "do",
    #                     "title": "updated task was: think about the future",
    #                     "detail": "",
    #                     "tid": "c21f969b5f.c9ec52c702.d06267f230"
    #                 },
    #             ]
    #         }
    #     ]
    # }
    #
    # endeavor_id = endeavors.insert_one(endeavor).inserted_id
    # collections = db.list_collection_names()
    #
    # print(f"Mongo! endeavor inserted_id: {endeavor_id} collections {collections}")
    # pprint.pprint(endeavors.find_one())
    #
    # print(f"The endeavors collection has {endeavors.count_documents({})} endeavors: ")
    # for endeavor in endeavors.find():
    #     pprint.pprint(endeavor)
    #
    # endeavors.update_one({'_id': endeavor_id}, {"$set": endeavor1}, upsert=True)
    # print(f"The updated endeavors collection has {endeavors.count_documents({})} endeavors: ")
    for endeavor in endeavors.find():
        pprint.pprint(endeavor)

    print(f"Now deleting all the endeavors")
    endeavors.delete_many({})
    print(f"After delete, the endeavors collection has {endeavors.count_documents({})} endeavors: ")
