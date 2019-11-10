l = [
    {'id':1,'parent_id':0},
    {'id':2,'parent_id':1},
    {'id':3,'parent_id':0},
    {'id':4,'parent_id':3},
    {'id':5,'parent_id':1},
    {'id':6,'parent_id':1},
    {'id':7,'parent_id':3},
    {'id':8,'parent_id':3},
    {'id':9,'parent_id':0},
]
#时间复杂度较高
def merge(target):
    result = []
    for dic in target:
        if dic['parent_id'] == 0:
            result.append({'id':dic['id']})
    for i in result:
        i['children'] = []
        for j in target:
            if i['id'] == j['parent_id']:
                i['children'].append({'id':j['id']})
    return result
#时间复杂度极低
def find_father(input_list):
    home = {}
    parent_list = []
    for data in input_list:
        if data['parent_id'] == 0:
            parent_list.append({'id':data['id']})
        else:
            p_id = data['parent_id']
            # if p_id not in home:
            #     home[p_id] = []
            #     home[p_id].append({'id':data['id']})
            # else:
            #     home[p_id].append({'id': data['id']})
            home.setdefault(p_id,[])
            home[p_id].append({'id': data['id']})
    for f in parent_list:
        if f['id'] in home:
            f['children'] = home[f['id']]
    return parent_list




if __name__ == '__main__':
    print(merge(l))
    print(find_father(l))
