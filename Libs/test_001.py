from UserESA import UserESA

u = UserESA(fname="dummy.xlsx", root_dir=".")

print(u._serialize_list_for_csv(None))
print(u._serialize_list_for_csv([]))
print(u._serialize_list_for_csv([5.0]))
print(u._serialize_list_for_csv([5.0, 10.0, 20.0]))