from ECHA import ESAloaderAPI as ESAloaderAPI
import json

exid ="ZOO_rikenbl_BL45XU_2026022612000000"

echa_esa = ESAloaderAPI.ESAloaderAPI(exid)

def updateDBinfo(cond, param_name, param_value):
    # ECHAを利用している場合
    zoo_samplepin_id = cond['zoo_samplepin_id']
    # param_name="isDone"の場合には zoo_samplepin を更新する必要がある
    if param_name == "isDone":
        p_index = cond['p_index']
        print(f"p_index={p_index} zoo_samplepin_id={zoo_samplepin_id}")
        echa_esa.setDone(p_index, zoo_samplepin_id, param_value)
    else:
        # JSON
        param_json = {
            param_name: param_value
        }
        param_json = {
            "data": json.dumps([{
                param_name: param_value
        }])
        }
        echa_esa.postResult(zoo_samplepin_id, param_json)

cond = {"zoo_samplepin_id": 304, "p_index": 0}

#updateDBinfo(cond, "flux", 1.0E12)
#updateDBinfo(cond, "t_meas_time", "UNKO")
#updateDBinfo(cond, "t_meas_start", "UNKO")
updateDBinfo(cond,"p_index", 999)

