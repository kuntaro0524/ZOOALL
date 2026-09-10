from ESAloaderAPI import ESAloaderAPI

exid = "ZOO_target_BL32XU_202603111407_echatest"

api = ESAloaderAPI(exid)
api.prep()

df = api.getResult(339)
print(df[["result_name", "value", "zoo_samplepin_id"]])

df = api.getSamplePin()
print(df[df["id"] == 339][["id", "isDone", "p_index", "isSkip"]])